import logging

from mercury.common.asyncio.endpoints import (
    StaticEndpointController, async_endpoint
)

from mercury.common.exceptions import EndpointError, MercuryUserError
from mercury.common.mongo import serialize_object_id

from mercury.rpc.jobs import Job, tasks

log = logging.getLogger(__name__)


class RPCController(StaticEndpointController):
    def __init__(self, inventory_client, jobs_collection, tasks_collection):
        super(RPCController, self).__init__()

        self.inventory_client = inventory_client
        self.jobs_collection = jobs_collection
        self.tasks_collection = tasks_collection

    @staticmethod
    def prepare_for_serialization(obj):
        """Converts object_id to a string and a datetime object to ctime format
        :param obj: probably a task or a job document
        :return: the object reference
        """
        serialize_object_id(obj)
        if obj.get('ttl_time_completed'):
            obj['ttl_time_completed'] = obj['ttl_time_completed'].ctime()
        return obj

    @async_endpoint('get_job')
    async def get_job(self, job_id, projection=None):
        """Gets a job from the job_collection. Jobs expire quickly.

        :param job_id: The Id of the job to get
        :param projection: A mongodb projection. https://goo.gl/kB2g26
        :return: A job object
        """
        job = await self.jobs_collection.find_one({'job_id': job_id},
                                                  projection=projection)
        if not job:
            return

        return self.prepare_for_serialization(job)

    @async_endpoint('get_job_status')
    async def get_job_status(self, job_id):
        """Get the status of job tasks

        :param job_id: the id of a job
        :return: Job object contain task status objects or None
        """
        error_states = ['ERROR', 'TIMEOUT', 'EXCEPTION']
        job = await self.jobs_collection.find_one({'job_id': job_id})
        if not job:
            return

        tasks = self.tasks_collection.find(
            {'job_id': job_id}, {'task_id': 1, 'status': 1, '_id': 0})

        job['has_failures'] = False
        job['tasks'] = []

        async for task in tasks:
            job['tasks'].append(serialize_object_id(task))
            if task['status'] in error_states:
                job['has_failures'] = True

        return self.prepare_for_serialization(job)

    @async_endpoint('get_job_tasks')
    async def get_job_tasks(self, job_id, projection=None):
        """Get tasks belonging to a job

        :param job_id: The id of a job (UUID)
        :param projection: A mongodb projection. https://goo.gl/kB2g26
        :return: dictionary containing top level keys count and jobs
        """
        c = self.tasks_collection.find({'job_id': job_id},
                                       projection=projection)
        count = await c.count()
        tasks = []
        async for task in c:
            tasks.append(self.prepare_for_serialization(task))

        return {'count': count, 'tasks': tasks}

    @async_endpoint('get_task')
    async def get_task(self, task_id):
        """Get a single task

        :param task_id: The id of the task (UUID)
        :return: The task object (dict)
        """

        task = await self.tasks_collection.find_one({'task_id': task_id})

        if not task:
            return

        return self.prepare_for_serialization(task)

    @async_endpoint('get_jobs')
    async def get_jobs(self, projection=None):
        """Get active jobs. The jobs collection is made ephemeral via a ttl key;
        this collection should not grow very large

        :param projection: A mongodb projection. https://goo.gl/kB2g26
        :return: dictionary containing top level keys count and jobs
        """
        projection = projection or {'instruction': 0}
        c = self.jobs_collection.find({}, projection=projection).sort(
            'time_created', 1)
        count = await c.count()
        jobs = []
        async for job in c:
            jobs.append(self.prepare_for_serialization(job))
        return {'count': count, 'jobs': jobs}

    @async_endpoint('create_job')
    async def create_job(self, query, instruction):
        """Create a job

        :param query: Query representing targets of the instruction
        :param instruction: An instruction or preprocessor directive. See the
        full documentation regarding instruction syntax at
        http://jr0d.github.io/mercury_api
        :raises EndpointException: Raised after catching a MercuryUserError as
        to conform to dispatch semantics
        :return: The job_id or None
        """

        # Add a constraint to the query that ensures we only match 'active'
        # devices (devices that are accessible through an agent)
        query.update({'active': {'$ne': None}})

        active_matches = await self.inventory_client.query(
            query, projection={'active': 1, 'origin': 1}, limit=0,
            sort_direction=1)

        active_matches = active_matches['message']['items']

        log.debug(f'Found {len(active_matches)} for query {query}')

        if not active_matches:
            return

        try:
            job = Job(instruction, active_matches, self.jobs_collection,
                      self.tasks_collection)
        except MercuryUserError as mue:
            raise EndpointError(str(mue), 'create_job')

        await job.insert()
        job.enqueue_tasks()

        return {'job_id': str(job.job_id)}

    @async_endpoint('update_task')
    async def update_task(self, update_data):
        self.validate_required(['task_id'], update_data)
        return await tasks.update_task(update_data, self.tasks_collection)

    @async_endpoint('complete_task')
    async def complete_task(self, return_data):
        self.validate_required(['task_id',
                                'job_id',
                                'status',
                                'message'], return_data)
        return await tasks.complete_task(return_data,
                                         self.jobs_collection,
                                         self.tasks_collection)
