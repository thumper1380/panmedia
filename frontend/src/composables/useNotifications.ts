import { computed, ref } from "vue"
import dayjs from "@/utils/dayjs"

type NotificationType = "message" | "reminder" | "alert" | "news" | string

interface Notification {
	id: number
	type: NotificationType
	title: string
	description: string
	read: boolean
	created_at: string
	action?: () => void
}

import { listNotifications } from "@/services/notificationService";


const items: Notification[] = [
	{
		id: 1,
		type: "message",
		title: "New Email",
		description: "Important document to read",
		read: false,
		created_at: "Today"
	},
	{
		id: 2,
		type: "reminder",
		title: "Appointment",
		description: "Meeting with client at 3:00 PM",
		read: false,
		created_at: "Yesterday"
	},
	{
		id: 9,
		type: "alert",
		title: "Alert",
		description: "Limited-time super offer on desired product",
		read: true,
		created_at: "Yesterday"
	},
	{
		id: 5,
		type: "news",
		title: "News",
		description: "Networking event in your city",
		read: false,
		created_at: dayjs().subtract(3, "d").format("D MMM")
	},
	{
		id: 3,
		type: "reminder",
		title: "Reminder",
		description: "Overdue bill payment",
		read: true,
		created_at: dayjs().subtract(7, "d").format("D MMM")
	},
	{
		id: 4,
		type: "reminder",
		title: "Deadline",
		description: "Submit report by tomorrow",
		read: true,
		created_at: dayjs().subtract(2, "d").format("D MMM")
	},
	{
		id: 6,
		type: "message",
		title: "Message",
		description: "New comment on your post",
		read: false,
		created_at: dayjs().subtract(4, "d").format("D MMM")
	},
	{
		id: 7,
		type: "reminder",
		title: "Reminder",
		description: "Complete purchase in your online cart",
		read: false,
		created_at: dayjs().subtract(5, "d").format("D MMM")
	},
	{
		id: 8,
		type: "reminder",
		title: "Invitation",
		description: "Friend's birthday party",
		read: true,
		created_at: dayjs().subtract(6, "d").format("D MMM")
	}
]

const list = ref<Notification[]>([])

const notifications = ref<Notification[]>([]);



for (let i = 0;i < 30;i++) {
	const item = items[i % items.length]
	item.id = i

	if (i > 2) {
		item.created_at = dayjs().subtract(i, "d").format("D MMM")
	}

	list.value.push({ ...item })
}

export function useNotifications() {
	const hasNotifications = computed(() => list.value.filter(o => !o.read).length !== 0)

	const fetchNotifications = async () => {
		try {
			const response = await listNotifications();
			notifications.value = response.data;
		} catch (error) {
			console.error('Error fetching notifications:', error);
			// Handle error appropriately, e.g., show user feedback
		}
	};
	const hasUnreadNotifications = computed(() =>
		notifications.value.some(notification => !notification.read));

	const setAllRead = () => {
		notifications.value.forEach(notification => notification.read = true);
	};

	const prependNotification = (newNotification: Notification) => {
		notifications.value = [newNotification, ...notifications.value];
	};

	const markAsRead = (notificationId: number) => {
		const notification = notifications.value.find(n => n.id === notificationId);
		if (notification) notification.read = true;
	};

	return {
		list,
		hasNotifications,
		prepend: (newItem: Notification) => {
			list.value = [newItem, ...list.value]
		},
		fetchNotifications,
		hasUnreadNotifications,
		setAllRead,
		prependNotification,
		markAsRead,
		notifications
	}
}
