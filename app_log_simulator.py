#!/usr/bin/env python3

import os
import sys
import yaml
import time
import random
import signal
import threading
import logging
import re
import uuid
from datetime import datetime

# ============================================================
# Application version
# ============================================================

APP_NAME = "AppLog-Simulator"

APP_VERSION = "1.1"

RELEASE_DATE = "2026-07-16"

# ============================================================
# Global settings
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_DIR = os.path.join(BASE_DIR, "config")

RUNNING = True

LOG_FILE = os.environ.get(
    "LOG_FILE",
    "logs/fake-log-generator.log"
)

# ============================================================
# Internal logging
# ============================================================

logging.basicConfig(
    #filename="/tmp/fake-log-generator.log",
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


# ============================================================
# Helpers
# ============================================================

def signal_handler(sig, frame):
    global RUNNING

    print("\nStopping generator...")
    logging.info("Shutdown requested")

    RUNNING = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)



def load_yaml(filename):

    with open(filename, "r") as f:
        return yaml.safe_load(f)



def ensure_directory(filename):

    directory = os.path.dirname(filename)

    if directory:
        os.makedirs(directory, exist_ok=True)



def now_string():

    return datetime.now().strftime("%b %d %H:%M:%S")



def random_pid():

    return random.randint(1000, 999999)



def random_ip():

    return ".".join(
        str(random.randint(1, 254))
        for _ in range(4)
    )



def random_guid():

    return str(uuid.uuid4())



# ============================================================
# Log level selection
# ============================================================


def select_level(probability):

    value = random.randint(1, 100)

    current = 0

    for level, percent in probability.items():

        current += percent

        if value <= current:
            return level


    return "INFO"



# ============================================================
# Generic messages
# ============================================================


INFO_MESSAGES = [

    "Application started successfully",

    "Configuration loaded",

    "Database connection established",

    "Processing request",

    "Worker thread started",

    "Heartbeat received",

    "Task completed successfully",

    "Health check OK"

]


WARNING_MESSAGES = [

    "Slow response detected",

    "Retrying failed operation",

    "Connection timeout, retry scheduled",

    "High memory usage detected",

    "External service response delayed"

]


ERROR_MESSAGES = [

    "Unable to connect to database",

    "Connection refused",

    "Unexpected application error",

    "Request processing failed",

    "Unhandled exception occurred"

]


CRITICAL_MESSAGES = [

    "Application crashed",

    "Database unavailable",

    "Fatal system error",

    "Service stopped unexpectedly"

]

# ============================================================
# Scenario Engine
# ============================================================


SCENARIOS = {


    "database_failure": [

        "ERROR Database connection failed",

        "ERROR MySqlConnector.MySqlException: Unable to connect to database",

        "ERROR Connection timeout expired",

        "ERROR Database server is unreachable",

        "ERROR at Database.Connection.Open()"

    ],



    "disk_full": [

        "ERROR No space left on device",

        "ERROR Cannot write application data",

        "ERROR Filesystem usage exceeded 100%"

    ],



    "memory_leak": [

        "WARNING Memory usage exceeded 90%",

        "ERROR OutOfMemoryException",

        "ERROR Failed to allocate memory block",

        "ERROR Application terminated due to memory pressure"

    ],



    "network_timeout": [

        "ERROR Network connection timeout",

        "ERROR Remote host did not respond",

        "ERROR SocketException: Connection timed out"

    ],



    "authentication_failure": [

        "WARNING Invalid credentials",

        "ERROR Authentication failed",

        "ERROR Access denied for user",

        "ERROR Login rejected"

    ],



    "kafka_down": [

        "ERROR Kafka broker unavailable",

        "ERROR Failed to send message",

        "ERROR Broker connection lost",

        "ERROR Kafka producer stopped"

    ],



    "rabbitmq_unavailable": [

        "ERROR RabbitMQ connection refused",

        "ERROR Message queue unavailable",

        "ERROR Channel closed unexpectedly",

        "ERROR Cannot connect to RabbitMQ broker"

    ]

}

def generate_scenario_event(config):


    scenario=config.get(
        "scenario",
        {}
    )


    scenario_type=scenario.get(
        "type"
    )


    if not scenario_type:

        return []



    messages=SCENARIOS.get(
        scenario_type
    )


    if not messages:

        logging.warning(
            "Unknown scenario: %s",
            scenario_type
        )

        return []



    pid=random_pid()

    app=config["name"]


    header=(

        f"{now_string()} "
        f"testserver1 "
        f"{app}[{pid}]: "

    )


    result=[]


    #
    # create event block
    #

    for msg in messages:

        result.append(
            header + msg
        )


    return result

def generate_message(level):

    if level == "INFO":
        return random.choice(INFO_MESSAGES)

    if level == "WARNING":
        return random.choice(WARNING_MESSAGES)

    if level == "ERROR":
        return random.choice(ERROR_MESSAGES)

    if level == "CRITICAL":
        return random.choice(CRITICAL_MESSAGES)

    return "Unknown event"



# ============================================================
# Template processing
# ============================================================


def replace_variables(line, app_name):

    replacements = {

        "{DATE}": now_string(),

        "{HOST}": "testserver1",

        "{PID}": str(random_pid()),

        "{APP}": app_name,

        "{IP}": random_ip(),

        "{GUID}": random_guid(),

        "{LINE}": str(random.randint(10,999))

    }


    for old,new in replacements.items():

        line = line.replace(old,new)


    return line

# ============================================================
# Smart/template helpers
# ============================================================


def load_example_lines(filename):

    try:

        with open(filename, "r") as f:
            lines = f.readlines()

        return [
            x.rstrip("\n")
            for x in lines
            if x.strip()
        ]

    except Exception as e:

        logging.error(
            "Cannot read example log %s: %s",
            filename,
            e
        )

        return []



def generate_stacktrace(app_name):

    templates = [

        "at {APP}.Core.Database.Connect() in /src/{APP}/Database.cs:line {LINE}",

        "at {APP}.Services.Worker.Execute() in /src/{APP}/Worker.cs:line {LINE}",

        "at {APP}.Program.Main() in /src/{APP}/Program.cs:line {LINE}",

    ]


    count = random.randint(3,8)

    result=[]


    for i in range(count):

        line=random.choice(templates)

        result.append(
            replace_variables(line, app_name)
        )


    return result



# ============================================================
# Event generators
# ============================================================


def generate_generic_event(config):

    app = config["name"]


    probability = config.get(
        "probability",
        {
            "INFO":90,
            "WARNING":8,
            "ERROR":2,
            "CRITICAL":0
        }
    )


    level = select_level(probability)


    pid=random_pid()


    header = (
        f"{now_string()} "
        f"testserver1 "
        f"{app}[{pid}]: "
    )


    event=[]


    message=generate_message(level)


    event.append(
        header +
        level +
        " " +
        message
    )


    #
    # ERROR and CRITICAL produce stack trace
    #

    if level in ["ERROR","CRITICAL"]:

        for line in generate_stacktrace(app):

            event.append(
                header +
                line
            )


    return event



# ============================================================
# Template mode
# ============================================================


def generate_template_event(config):


    example=config.get("example_log")


    if not example:

        return generate_generic_event(config)



    lines=load_example_lines(example)


    if not lines:

        return generate_generic_event(config)



    #
    # take random block
    #

    start=random.randint(
        0,
        len(lines)-1
    )


    block_size=random.randint(
        1,
        min(10,len(lines))
    )


    selected=lines[
        start:start+block_size
    ]


    result=[]


    for line in selected:

        result.append(
            replace_variables(
                line,
                config["name"]
            )
        )


    return result



# ============================================================
# Smart mode
# ============================================================


def generate_smart_event(config):


    probability=config.get(
        "probability",
        {}
    )


    level=select_level(probability)



    #
    # Mostly use templates from real log
    #

    if level in ["ERROR","CRITICAL"]:

        lines=load_example_lines(
            config.get("example_log")
        )


        if lines:

            result=[]


            for line in random.sample(
                lines,
                min(
                    random.randint(3,8),
                    len(lines)
                )
            ):

                result.append(
                    replace_variables(
                        line,
                        config["name"]
                    )
                )


            return result



    #
    # Otherwise normal event
    #

    return generate_generic_event(config)



# ============================================================
# Select generator
# ============================================================


def generate_event(config):


    mode=config.get(
        "mode",
        "generic"
    )


    if mode=="generic":

        return generate_generic_event(config)


    if mode=="template":

        return generate_template_event(config)


    if mode=="smart":

        return generate_smart_event(config)



    logging.warning(
        "Unknown mode %s, using generic",
        mode
    )


    return generate_generic_event(config)



# ============================================================
# Write event
# ============================================================


def write_event(filename, lines):


    ensure_directory(filename)


    try:

        with open(
            filename,
            "a"
        ) as f:


            for line in lines:

                f.write(
                    line +
                    "\n"
                )


    except Exception as e:


        logging.error(
            "Cannot write %s: %s",
            filename,
            e
        )

# ============================================================
# Scenario scheduler
# ============================================================


def scenario_enabled(config):

    scenario = config.get(
        "scenario",
        {}
    )

    return scenario.get(
        "enabled",
        False
    )



def scenario_interval(config):

    scenario = config.get(
        "scenario",
        {}
    )

    return scenario.get(
        "every",
        3600
    )


# ============================================================
# Worker thread
# ============================================================


def worker(config):

    name = config.get(
        "name",
        "unknown"
    )


    output_log = config.get(
        "output_log"
    )


    if not output_log:

        logging.error(
            "%s: output_log missing",
            name
        )

        return



    interval = config.get(
        "interval",
        {}
    )


    min_interval = interval.get(
        "min",
        60
    )


    max_interval = interval.get(
        "max",
        300
    )



    #
    # Scenario settings
    #

    use_scenario = scenario_enabled(
        config
    )


    next_scenario_time = (
        time.time()
        +
        scenario_interval(config)
    )



    print(
        f"[{name}] started "
        f"mode={config.get('mode','generic')} "
        f"log={output_log}"
    )


    if use_scenario:

        print(
            f"[{name}] scenario="
            f"{config['scenario'].get('type')} "
            f"every="
            f"{scenario_interval(config)} sec"
        )



    logging.info(
        "%s started",
        name
    )



    while RUNNING:


        try:


            #
            # Check scenario timer
            #

            if (
                use_scenario
                and
                time.time() >= next_scenario_time
            ):


                event = generate_scenario_event(
                    config
                )


                if event:

                    write_event(
                        output_log,
                        event
                    )


                    logging.info(
                        "%s scenario executed: %s",
                        name,
                        config["scenario"]["type"]
                    )


                #
                # schedule next execution
                #

                next_scenario_time = (
                    time.time()
                    +
                    scenario_interval(config)
                )



            else:


                #
                # Normal application activity
                #

                event = generate_event(
                    config
                )


                write_event(
                    output_log,
                    event
                )


                logging.info(
                    "%s generated %d lines",
                    name,
                    len(event)
                )




        except Exception as e:


            logging.exception(
                "%s worker error: %s",
                name,
                e
            )



        #
        # sleep
        #

        sleep_time=random.randint(
            min_interval,
            max_interval
        )


        time.sleep(
            sleep_time
        )



    print(
        f"[{name}] stopped"
    )


# ============================================================
# Load configs
# ============================================================


def load_configs():


    configs=[]


    if not os.path.isdir(CONFIG_DIR):

        print(
            "Config directory not found:",
            CONFIG_DIR
        )

        sys.exit(1)



    for filename in os.listdir(CONFIG_DIR):


        if not filename.endswith(
            ".yaml"
        ):

            continue



        full_path=os.path.join(
            CONFIG_DIR,
            filename
        )


        try:

            config=load_yaml(
                full_path
            )


            configs.append(
                config
            )


            print(
                "Loaded:",
                filename
            )


        except Exception as e:

            logging.error(
                "Cannot load %s: %s",
                filename,
                e
            )



    return configs


# ============================================================
# Startup banner
# ============================================================

def print_banner():

    print("")
    print("=" * 55)
    print(
        f" {APP_NAME} v{APP_VERSION} "
        f"({RELEASE_DATE})"
    )
    print("=" * 55)
    print("")

# ============================================================
# Main
# ============================================================


def main():


    print_banner()

    configs=load_configs()



    if not configs:

        print(
            "No configs found"
        )

        sys.exit(1)



    threads=[]


    for config in configs:


        thread=threading.Thread(
            target=worker,
            args=(config,),
            daemon=True
        )


        thread.start()


        threads.append(
            thread
        )



    print(
        f"Running {len(threads)} log generators"
    )



    #
    # Wait
    #

    while RUNNING:

        time.sleep(1)



    print(
        "Waiting threads..."
    )


    for thread in threads:

        thread.join(
            timeout=5
        )



    print(
        "Bye"
    )



if __name__=="__main__":

    main()

    