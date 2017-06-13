import logging
import time
import uuid

from mercury.common.exceptions import MercuryUserError, MercuryCritical
from mercury.rpc.preprocessors import instruction_preprocessors

from mercury.rpc.jobs.tasks import Task

log = logging.getLogger(__name__)


class Job(object):
    def __init__(self, instruction, targets, jobs_collection, tasks_collection):
        """
        :param instruction: Procedure dictionary containing method, args, kwargs
        :param targets: active inventory targets
        :param collection: mongodb collection object (capped)
        :raises MercuryUserError: catch, log, demean, and move on
        :raises MercuryCritical: Halt and catch fire
        """
        self.instruction = instruction
        self.targets = targets
        self.jobs_collection = jobs_collection
        self.tasks_collection = tasks_collection

        self.preprocessor = None
        self.primitive = False

        self.job_id = uuid.uuid4()
        self.tasks = {}
        # Populate the tasks

        for target in targets:
            task = self.__create_task(target)
            self.tasks[str(task.task_id)] = task

        self.task_count = len(targets)

        self.time_started = None
        self.time_completed = None
        self.ttl_time_completed = None

    def __check_method(self, method):
        for target in self.targets:
            try:
                capabilities = target['capabilities']
            except KeyError:
                raise MercuryCritical('Encountered malformed target, the database is corrupted')
            if method not in capabilities:
                raise MercuryUserError('One of more targets does not support method: %s' % method)

    def __create_task(self, target):
        # TODO: select ipv4 or ipv6
        # TODO: add yaml option: prefer_ipv6 (bool)
        try:
            mercury_id = target['mercury_id']
            host = target['active']['rpc_address']
            port = target['active']['rpc_port']
        except KeyError:
            raise MercuryCritical('Encountered malformed target, the database is corrupted')

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

    def __insert_job(self):
        self.time_started = time.time()

        for task in list(self.tasks.values()):
            task.enqueue()

        log.info('Inserting job: %s' % self.job_id)

        self.jobs_collection.insert_one(self.to_dict())
        self.tasks_collection.insert_many([task.to_dict() for task in list(self.tasks.values())])

    def start(self):
        self.__insert_job()
