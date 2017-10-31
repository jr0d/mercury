# Mercury Logging service

Intended to provide mercury logging and dispatching capabilities for agents. Agents on an internal provisioning network may not be able to easily log to external services. As such, this service can be stood up parallel to the other backend services and be used to receive logging message from the agent.

# Agent configuration

https://github.com/jr0d/mercury-agent/blob/master/mercury-agent-sample.yaml#L13


# Agent implementation

https://github.com/jr0d/mercury-agent/blob/master/mercury/agent/remote_logging.py
