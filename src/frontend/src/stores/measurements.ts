import { defineStore } from "pinia";
import { ref } from "vue";
import type { SensorData } from "./sensorData";

export type Measurements = {
    pixPerInch: number,
    leftSide: number,
    rightSide: number,
    topSide: number,
    fullLen: number,
    fullHgt: number
}

let base: Measurements = {
    pixPerInch: 0,
    leftSide: 0,
    rightSide: 0,
    topSide: 0,
    fullLen: 0,
    fullHgt: 0
}

export const useMeasurementStore = defineStore('measurements', {
    state: () => ({ data: base }),
    actions: {
        setAll(val: Measurements) {
            this.data = val
        },
        getAll(): Measurements {
            return this.data
        }
    }
})