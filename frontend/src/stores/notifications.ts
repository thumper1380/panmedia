// src/stores/notificationStore.js
import { defineStore, acceptHMRUpdate } from "pinia";
import * as notificationService from "@/services/notificationService";

export const useNotificationStore = defineStore("notification", {
    state: () => ({
        notifications: [],
    }),
    actions: {
        async fetchNotifications() {
            try {
                const response = await notificationService.listNotifications();
                this.notifications = response.data;
            } catch (error) {
                console.error('Error fetching notifications:', error);
            }
        },
        async markAsRead(id: string) {
            try {
                await notificationService.read(id);
                // Optionally, update the state of the notification to 'read'
            } catch (error) {
                console.error('Error marking notification as read:', error);
            }
        },
        async markAllAsRead() {
            try {
                await notificationService.readAll();
                // Optionally, update all notifications in state to 'read'
            } catch (error) {
                console.error('Error marking all notifications as read:', error);
            }
        },
    },
    getters: {


    },
    // Optional: persistence logic...
});

if (import.meta.hot) {
    import.meta.hot.accept(acceptHMRUpdate(useNotificationStore, import.meta.hot));
}
