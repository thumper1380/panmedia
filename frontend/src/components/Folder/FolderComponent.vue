<template>
    <div class="email flex items-center" :class="{ selected: email.selected, seen: email.seen }" @click="select(email)">
        <div class=" flex">
            <FolderIcon type="RotationContolAffiliateFolder" />
        </div>
        <div class="title grow">
            <span class="name">
                Folder Name
            </span>
            <span class="subject">
                Affiliate is Company_Name
            </span>
        </div>
        <div class="attachments flex">
            <Icon :size="16" name="ion:edit"></Icon>
        </div>
    </div>
</template>

<script setup lang="ts">
import { NCheckbox, NAvatar, NButton } from "naive-ui"
import Icon from "@/components/common/Icon.vue"
import FolderIcon from "@/components/Tree/FolderIcon.vue"
import { type TreeFolderType } from "@/types/tree"

const StarActiveIcon = "carbon:star-filled"
const StarIcon = "carbon:star"
const TrashIcon = "carbon:trash-can"
const LabelIcon = "carbon:bookmark-filled"
const LabelOutIcon = "carbon:bookmark"
const AttachmentIcon = "carbon:attachment"
// const FolderIcon = "carbon:folder-move-to"
import { toRefs, computed, ref } from "vue"
import { useThemeStore } from "@/stores/theme"

defineOptions({
    name: "Email"
})



interface Email {
    id: string
    date: Date
    dateText?: string
    subject: string
    body: string
    seen: boolean
    starred: boolean
    folder: string
    labels: {
        id: string
        title: string
    }[]
    name: string
    email: string
    avatar: string
    attachments: { name: string; size: string }[]
    selected: boolean
}

const email = ref<Email>({
    id: "1",
    date: new Date(),
    subject: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
    body: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla euismod, nisl eget fermentum aliquam,",
    seen: false,
    starred: false,
    folder: "inbox",
    labels: [
        { id: "personal", title: "Personal" },
        { id: "office", title: "Office" },
        { id: "important", title: "Important" },
        { id: "shop", title: "Shop" }
    ],
    name: "John Doe",
    email: "abc@gmail.com",
    avatar: "https://i.pravatar.cc/150?img=1",
    attachments: [
        { name: "file1.jpg", size: "1.2MB" },
        { name: "file2.jpg", size: "1.2MB" },
        { name: "file3.jpg", size: "1.2MB" }
    ],
    selected: false
})


// const { email } = toRefs(props)

const emit = defineEmits<{
    (e: "select", value: Email): void
}>()

const themeStore = useThemeStore()

const primaryColor = computed(() => themeStore.primaryColor)
const secondaryColors = computed(() => themeStore.secondaryColors)

const labelsColors = {
    personal: secondaryColors.value["secondary1"],
    office: secondaryColors.value["secondary2"],
    important: secondaryColors.value["secondary3"],
    shop: secondaryColors.value["secondary4"]
} as unknown as { [key: string]: string }

function select(email: Email) {
    emit("select", email)
}

// function toggleCheck(email: Email) {
// 	mailboxStore.toggleCheck(email)
// }

// function toggleStar(email: Email) {
// 	mailboxStore.toggleStar(email)
// }
</script>

<style lang="scss" scoped>
.email {
    height: 52px;
    padding: 0 30px;
    border-bottom: var(--border-small-050);
    gap: 18px;
    line-height: 1.2;
    white-space: nowrap;
    cursor: pointer;
    transition: all 0.1s ease-in;
    container-type: inline-size;

    .title {
        overflow: hidden;
        width: 0;
        text-overflow: ellipsis;
        font-size: 15px;

        .name {
            margin-right: 14px;
        }

        .subject {
            font-weight: bold;
        }
    }

    .actions {
        // display: none;
    }

    &.seen {
        background-color: var(--bg-secondary-color);

        .title {
            opacity: 0.85;

            .subject {
                font-weight: normal;
            }
        }
    }

    &.selected {
        background-color: var(--primary-005-color);
    }

    &:hover {
        box-shadow: 0px 0px 0px 1px var(--primary-050-color) inset;

        .actions {
            display: flex;
        }

        .labels,
        .attachments,
        .date {
            // display: none;
        }
    }

    @container (max-width: 760px) {
        .title {
            display: flex;
            flex-direction: column;

            .name,
            .subject {
                overflow: hidden;
                text-overflow: ellipsis;
            }
        }
    }

    @container (max-width: 500px) {
        .avatar {
            display: none;
        }
    }

    @container (max-width: 360px) {
        .labels {
            display: none;
        }
    }
}

@media (max-width: 700px) {
    .email {
        gap: 14px;
        padding: 0 20px;

        .title {
            font-size: 14px;
        }
    }
}
</style>
