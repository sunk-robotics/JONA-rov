import { defineStore } from "pinia";

export const useImageStore = defineStore('image', {
    state: (): { image: ArrayBuffer | null } => ({ image: null }),
    actions: {
        set(data: ArrayBuffer) {
            this.image = data
        },
        get(): ArrayBuffer {
            return this.image
        }
    }
})