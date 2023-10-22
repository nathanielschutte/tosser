from enum import Enum



class IngestState(Enum):
    IDLE = 'idle' # before run

    READING = 'reading'
    GENERATING = 'generating'
    TRANSACTING = 'transacting'

    WAITING = 'waiting' # for last response

    DONE = 'done'
