

<template>
    <n-card :title="title" class="mt-4">
        <n-scrollbar trigger="hover" x-scrollable>
            <div style="white-space: nowrap; margin-bottom: 15px">
                <n-timeline :horizontal="true" class="mt-4">
                    <n-timeline-item v-for="log in stateLog" :key="log.id" :type="mapLogTypeToTimelineType(log)"
                        :title="log.type" :time="DateToString(log.created_at)">
                        <template #header>
                            <n-tag :type="mapLogTypeToTimelineType(log)" size="small">{{ mapLogTypeToTitle(log.type)
                            }}</n-tag>
                        </template>
                        <template #default>
                            <p v-if="log.type === 'StateSwitchedLog'">
                                State switched from <strong>{{ log.source_state }}</strong> to <strong>{{ log.target_state
                                }}</strong>
                            </p>
                            <p v-if="log.type === 'StateInitiatedLog'">
                                State initiated with <strong>{{ log.initial_state }}</strong> status
                            </p>
                            <p v-if="log.type === 'PushingErrorLog' || log.type === 'PushingAttemptLog'">
                            <div class="copy" @click="CopyText(log.message)">
                                <n-ellipsis class="clickable" :tooltip="{
                                    placement: 'top', showArrow: true, trigger: 'hover',
                                }" style="max-width: 350px;">
                                    <span style="font-size: 14px; font-family: monospace;">
                                        {{ log.message }}
                                    </span>
                                </n-ellipsis>
                            </div>


                            </p>
                        </template>
                    </n-timeline-item>
                </n-timeline>

            </div>

        </n-scrollbar>

    </n-card>
</template>


<script setup lang="ts">
// import naive ui components
import { NCard, NTag, NTimeline, NTimelineItem, NScrollbar, NAlert, NEllipsis, NCode, NButton } from 'naive-ui';
import { h, ref } from 'vue';
import type { StateLog, StateInitiatedLog } from '@/types/trafficdata';
import dayjs from "@/utils/dayjs"
import { useNotification, useMessage } from 'naive-ui';
import type { MessageProviderProps } from 'naive-ui'

// import color types from naive ui
const notification = useNotification();
const message = useMessage();

const props = defineProps<{
    stateLog: StateLog[];
    title: string;
}>();



const DateToString = (date: string): string => {
    return dayjs(date).format('YYYY-MM-DD HH:mm:ss');
};

interface Item {
    placement: MessageProviderProps['placement']
    text: string
}

const placement = ref<MessageProviderProps['placement']>('top-right')

const CopyText = (text: string) => {
    navigator.clipboard.writeText(text);
    // naive ui message copy to clipboard
    message.success('Copied to clipboard', {
        duration: 2000,
    })

};

// StateInitiatedLog > State Initiated, StateSwitchedLog > State Switched, PushingAttemptLog > Pushing Attempt, PushingErrorLog > Pushing Error
// map this 
const mapLogTypeToTitle = (logType: string): string => {
    switch (logType) {
        case 'StateInitiatedLog':
            return 'State Initiated';
        case 'StateSwitchedLog':
            return 'State Switched';
        case 'PushingAttemptLog':
            return 'Pushing Attempt';
        case 'PushingErrorLog':
            return 'Pushing Error';
        default:
            return logType; // Fallback to the original type if no match is found
    }
};




const mapLogTypeToTimelineType = (log: StateLog): string => {
    switch (log.type) {
        case 'StateInitiatedLog':
            return 'success';
        case 'StateSwitchedLog':
            return 'info';
        case 'PushingAttemptLog':
            return 'warning';
        case 'PushingErrorLog':
            return 'error';
        default:
            return 'default';
    }
};
</script>

<style lang="scss" scoped>
.copy {
    cursor: pointer;
}

.n-tag {
    text-transform: uppercase;
}
</style>