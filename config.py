# config.py

DB_NAME = "aas_db"
DB_USER = "postgres"
DB_PASSWORD = "omnifactory1234"
DB_HOST = "localhost"
DB_PORT = 5432

# Template of submodel names and their keys for MiRs
MIR_SUBMODEL_TEMPLATE = {
    "OperationalData": [
        "mode_text",
        "state_text",
        "battery_percentage",
        "battery_time_remaining",
        "velocity",
        "velocityAngular"
    ],
    "NavigationAndMission": [
        "mission_queue_id",
        "mission_text",
        "moved",
        "distance_to_next_target",
        "positionX",
        "positionY",
        "orientation"
    ],
    "ConfigurationAndSettings": [
        "joystick_low_speed_mode_enabled",
        "safety_system_muted",
        "unloadedMapChanges"
    ]
}

# Template of submodel names and their keys for KUKA robots
KUKA_SUBMODEL_TEMPLATE = {
    "Operational_Data": [
        "battery_state",
        "robot_runtime",
        "velocity",
        "acceleration",
        "load"
    ],
    "Navigation_Data": [
        "position",
        "tool_status",
        "orientation"
    ],
    "Mission_Data": [
        "number_of_missions",
        "timer"
    ],
    "Process_Data": [
        "motion_state",
        "distance_to_next",
        "program_state"
    ]
}
