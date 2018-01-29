import logging
import time
import uuid

from mercury.common.exceptions import MercuryUserError, MercuryCritical
from mercury.common.helpers import util
from mercury.common.transport import format_zurl
from mercury.rpc.preprocessors import instruction_preprocessors

from mercury.rpc.backend_clients import get_queue_manager
from mercury.rpc.jobs.tasks import Task


log = logging.getLogger(__name__)


class Job(object):
    def __init__(self, instruction, targets, jobs_collection, tasks_collection,
                 job_id=None):
        """
        :param instruction: Procedure dictionary containing method, args, kwargs
        :param targets: active inventory targets
        :param jobs_collection: Job MongoDB collection object
        :param tasks_collection: Tasks MongoDB collection object
        :param job_id: Use this job_id rather than generating one
        :raises MercuryUserError: catch, log, demean, and move on
        :raises MercuryCritical: Halt and catch fire
        """
        self.instruction = instruction
        self.targets = targets
        self.jobs_collection = jobs_collection
        self.tasks_collection = tasks_collection

        self.preprocessor = None
        self.primitive = False

        self.job_id = job_id or uuid.uuid4()
        self.tasks = {}
        # Populate the tasks

        for target in targets:
            task = self.create_task(target)
            self.tasks[str(task.task_id)] = task

        self.task_count = len(targets)

        self.time_started = None
        self.time_completed = None
        self.ttl_time_completed = None

    def check_method(self, method):
        for target in self.targets:
            try:
                capabilities = target['capabilities']
            except KeyError:
                raise MercuryCritical('Encountered malformed target, the '
                                      'database is corrupted')
            if method not in capabilities:
                raise MercuryUserError('One of more targets does not support '
                                       'method: %s' % method)

    def create_task(self, target):
        # TODO: select ipv4 or ipv6
        # TODO: add yaml option: prefer_ipv6 (bool)
        try:
            mercury_id = target['mercury_id']
            host = target['active']['rpc_address']
            port = target['active']['rpc_port']
            backend = format_zurl(target['origin']['address'],
                                  target['origin']['port'])
        except KeyError:
            raise MercuryCritical('Encountered malformed target, the database '
                                  'is corrupted')

        # Preprocessor entry

        method = self.instruction.get('method')
        if method:
            self.primitive = True
            call_data = {
                'method': self.instruction['method'],
                'args': self.instruction.get('args', []),
                'kwargs': self.instruction.get('kwargs', {})
            }

        else:
            self.preprocessor = self.instruction.get('preprocessor')
            if not self.preprocessor:
                raise MercuryUserError('Contract invalid')

            preprocessor = instruction_preprocessors.get(self.preprocessor)
            if not preprocessor:
                raise MercuryUserError('Specified preprocessor does not exist')

            log.info('Calling %s preprocessor' % preprocessor['name'])
            call_data = preprocessor['entry'](target, self.instruction)

        task = Task(
            job_id=self.job_id,
            mercury_id=mercury_id,
            host=host,
            port=port,
            backend=backend,
            **call_data
        )

        log.debug('Created task: %s' % task)
        return task

    def to_dict(self):
        return {
            'job_id': str(self.job_id),
            'time_started': self.time_started,
            'time_completed': self.time_completed,
            'ttl_time_completed': self.ttl_time_completed,
            'instruction': self.instruction,
            'task_count': self.task_count
        }

    async def insert(self):
        self.time_started = time.time()

        await self.jobs_collection.insert_one(self.to_dict())
        await self.tasks_collection.insert_many(
            [task.to_dict() for task in list(self.tasks.values())])

    def enqueue_tasks(self):
        """ Uses backend manager processes to enqueue tasks """

        # Generate an index that relates backends to tasks
        backend_index = util.build_index_l([task.to_dict()
                                            for task in self.tasks.values()],
                                           'backend')

        # Loop through backends and get a queue backend manager
        for backend in backend_index:
            manager = get_queue_manager(backend)

            # Add each task to the managers queue
            for task in backend_index[backend]:
                manager.tasks_queue.put(task)
