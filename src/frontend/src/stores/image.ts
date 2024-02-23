import { defineStore } from "pinia";

export const useImageStore = defineStore('image', {
    state: (): { image: VideoFrame | null } => ({ image: null }),
    actions: {
        set(data: VideoFrame) {
            this.image = data
        },
        get(): VideoFrame {
            return this.image
        }
    }
})