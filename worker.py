"""
Vast.ai PyWorker configuration for generic model server.

This is the PYWORKER_REPO entry point — cloned and run by Vast.ai's start_server.sh.
It proxies HTTP requests to a FastAPI model server running on localhost.

Environment variables:
    MODEL_SERVER_PORT   — port of the local model server (default: 18000)
    MAX_QUEUE_TIME      — max seconds a request can wait in queue (default: 30)
"""
import os
import uuid

from vastai import BenchmarkConfig, HandlerConfig, LogActionConfig, Worker, WorkerConfig

MODEL_SERVER_PORT = int(os.environ.get("MODEL_SERVER_PORT", "18000"))
MAX_SESSIONS = int(os.environ.get("MAX_SESSIONS", "1"))
PROCESS_MAX_QUEUE_TIME = float(os.environ.get("PROCESS_MAX_QUEUE_TIME", "300"))
PROCESS_PARALLEL_REQUESTS = True if os.environ.get("PROCESS_PARALLEL_REQUESTS", "false") == "true" else False
SUBMIT_MAX_QUEUE_TIME = float(os.environ.get("SUBMIT_MAX_QUEUE_TIME", "300"))
SUBMIT_PARALLEL_REQUESTS = True if os.environ.get("SUBMIT_PARALLEL_REQUESTS", "false") == "true" else False

def _benchmark_payload():
    return {"sleep": 10}

print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
print("MODEL_SERVER_PORT", MODEL_SERVER_PORT, "env: ", os.environ.get("MODEL_SERVER_PORT"))
print("MAX_SESSIONS", MAX_SESSIONS, "env: ", os.environ.get("MAX_SESSIONS"))
print("PROCESS_MAX_QUEUE_TIME", PROCESS_MAX_QUEUE_TIME, "env: ", os.environ.get("PROCESS_MAX_QUEUE_TIME"))
print("PROCESS_PARALLEL_REQUESTS", PROCESS_PARALLEL_REQUESTS, "env: ", os.environ.get("PROCESS_PARALLEL_REQUESTS"))
print("SUBMIT_MAX_QUEUE_TIME", SUBMIT_MAX_QUEUE_TIME, "env: ", os.environ.get("SUBMIT_MAX_QUEUE_TIME"))
print("SUBMIT_PARALLEL_REQUESTS", SUBMIT_PARALLEL_REQUESTS, "env: ", os.environ.get("SUBMIT_PARALLEL_REQUESTS"))
print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

worker_config = WorkerConfig(
    model_server_url="http://127.0.0.1",
    model_server_port=MODEL_SERVER_PORT,
    model_log_file="/var/log/model/server.log",
    max_sessions=MAX_SESSIONS,
    handlers=[
        # Sync handler — FIFO queue, has benchmark
        HandlerConfig(
            route="/process",
            allow_parallel_requests=PROCESS_PARALLEL_REQUESTS,
            max_queue_time=PROCESS_MAX_QUEUE_TIME,
            workload_calculator=lambda payload: 250 if payload.get("sleep") else 10000,
            benchmark_config=BenchmarkConfig(
                generator=_benchmark_payload,
                runs=1,
                concurrency=1,
                do_warmup=False,
            ),
        ),
        # Async submit — instant return, parallel OK
        HandlerConfig(
            route="/jobs/submit",
            allow_parallel_requests=SUBMIT_PARALLEL_REQUESTS,
            max_queue_time=SUBMIT_MAX_QUEUE_TIME,
            workload_calculator=lambda payload: 100.0,
        ),
        # Async poll — instant return, parallel OK, zero cost
        HandlerConfig(
            route="/jobs/status",
            allow_parallel_requests=True,
            max_queue_time=SUBMIT_MAX_QUEUE_TIME,
            workload_calculator=lambda payload: 0.0,
        ),
    ],
    log_action_config=LogActionConfig(
        on_load=["Application startup complete."],
        on_error=[
            "CUDA error:",
            "error from cudaGetDeviceCount"
        ],
    ),
)

if __name__ == "__main__":
    print("MODEL_SERVER_PORT", MODEL_SERVER_PORT, "env: ", os.environ.get("MODEL_SERVER_PORT"))
    print("MAX_SESSIONS", MAX_SESSIONS, "env: ", os.environ.get("MAX_SESSIONS"))
    print("PROCESS_MAX_QUEUE_TIME", PROCESS_MAX_QUEUE_TIME, "env: ", os.environ.get("PROCESS_MAX_QUEUE_TIME"))
    print("PROCESS_PARALLEL_REQUESTS", PROCESS_PARALLEL_REQUESTS, "env: ", os.environ.get("PROCESS_PARALLEL_REQUESTS"))
    print("SUBMIT_MAX_QUEUE_TIME", SUBMIT_MAX_QUEUE_TIME, "env: ", os.environ.get("SUBMIT_MAX_QUEUE_TIME"))
    print("SUBMIT_PARALLEL_REQUESTS", SUBMIT_PARALLEL_REQUESTS, "env: ", os.environ.get("SUBMIT_PARALLEL_REQUESTS"))
    Worker(worker_config).run()
