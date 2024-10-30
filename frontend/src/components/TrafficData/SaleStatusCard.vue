<template>
    <n-card :title="title" class="mt-4">
        <n-data-table :data="saleStatusLog" :columns="saleStatusColumns"></n-data-table>
    </n-card>
</template>


<script setup lang="ts">

import { NCard, NDataTable, NTag } from 'naive-ui';
import { ref, h, onBeforeMount } from 'vue';
import type { SaleStatusLog } from '@/types/trafficdata';
import dayjs from "@/utils/dayjs"

const props = defineProps<{
    saleStatusLog: SaleStatusLog[],
    title: string;
}>();


const saleStatusColumns = ref([
    {
        title: 'Created At', 
        key: 'created_at',
        render: (row: any) => h('span', dayjs(row.created_at).format('YYYY-MM-DD HH:mm:ss'))
    },
    {
        title: 'Status', key: 'status',
        // render as tag
        render: (row: any) => h(NTag, {
            // type - if it's new - success, if it's callback - warning, if it's rejected - error
            type: row.status === 'New' ? 'success' : row.status === 'Callback' ? 'warning' : 'error',
            size: 'small',
        }, { default: () => row.status })
    },
]);
</script>



