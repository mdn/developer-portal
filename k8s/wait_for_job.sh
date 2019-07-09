#!/bin/bash

GET_JOB_JSON="kubectl -n ${K8S_NAMESPACE} get job ${JOB_NAME} -o json"

check_job() {
    echo "Checking..."
    ${GET_JOB_JSON} | jq -e '(.status.succeeded != null) or (.status.failed != null)'
}

wait_for_job() {
    echo "Waiting for job \"${JOB_NAME}\" to complete..."
    until check_job
    do
      sleep 1
    done
    # Set the exit status based on the job's status.
    if ${GET_JOB_JSON} | jq -e '(.status.succeeded != null)'
    then
        echo "Job \"${JOB_NAME}\" was successful!"
        exit 0
    else
        echo "Job \"${JOB_NAME}\" failed!"
        exit 1
    fi;
}

# Wait until the job completes (succeeds or fails), and
# return the exit status based on the status of the job.
wait_for_job
