import { defineStore } from "pinia"

type SensorData = {
    internal_temp: number | null,
    external_temp: number | null,
    temp: number | null, 
    depth: number | null,
    yaw: number | null,
    roll: number | null,
    pitch: number | null,
    voltage_5V: number | null,
    current_5V: number | null,
    voltage_12V: number | null,
    current_12V: number | null,
    x_accel: number | null,
    y_accel: number | null,
    z_accel: number| null,
    speed_multiplier: number | null,
    depth_anchor_enabled: boolean | null,
    yaw_anchor_enabled: boolean | null,
    roll_anchor_enabled: boolean | null,
    pitch_anchor_enabled: boolean | null,
    motor_lock_enabled: boolean | null
}

let base: SensorData = {
    internal_temp: null,
    external_temp: null,
    temp: null, 
    depth: null,
    yaw: null,
    roll: null,
    pitch: null,
    voltage_5V: null,
    current_5V: null,
    voltage_12V: null,
    current_12V:  null,
    x_accel:  null,
    y_accel:  null,
    z_accel:  null,
    speed_multiplier:  null,
    depth_anchor_enabled:  null,
    yaw_anchor_enabled:  null,
    roll_anchor_enabled:   null,
    pitch_anchor_enabled:   null,
    motor_lock_enabled:   null
}

export const useSensorDataStore = defineStore('sensor-data', {
    state: () => ({ data: base, history: [] as { data: SensorData, timestamp: number}[]}),
    actions: {
        setAll(val: SensorData) {
            this.data = val
            this.history = []
        },
        getAll() {
            return this.data
        },
        get(field: keyof SensorData) {
            return this.data[field]
        },
        updateHistory() {
            this.history.push({ data: this.data, timestamp: Date.now() })
        }
    }
})