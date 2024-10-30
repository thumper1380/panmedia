<template>
    <div class="page">

        <ModelDetial :detail-response="detailResponse" title="Click Detail" />

        <StateLogCard title="State Log" :state-log="stateLog" />

        <SaleStatusCard title="Advertiser Sale Statuses" :sale-status-log="saleStatusLog" />
    </div>
</template>
  
<script setup lang="ts">
import { ref, h, onBeforeMount } from 'vue';
import { useDialog, useMessage, } from 'naive-ui';
import type { StateLog, SaleStatusLog } from '@/types/trafficdata';
import { statelog as fetchStateLog, salestatuslog as fetchSaleStatusLog, retrieve as fetchDetail } from '@/services/trafficdataService';
import { useRoute } from 'vue-router';
import StateLogCard from '@/components/TrafficData/StateLogCard.vue';
import SaleStatusCard from '@/components/TrafficData/SaleStatusCard.vue';
import ModelDetial from '@/components/common/Model/ModelDetailView.vue';
import type { ApiResponse } from '@/types/response';
import type { TrafficData } from '@/types/trafficdata';
const message = useMessage();
const dialog = useDialog();
const router = useRoute();


const stateLog = ref<StateLog[]>([]);
const saleStatusLog = ref<SaleStatusLog[]>([]);



const detailResponse = ref<ApiResponse<TrafficData>>({} as ApiResponse<TrafficData>);

onBeforeMount(async () => {
    try {
        const { id } = router.params;
        // Fetch detail
        const response = await fetchDetail(id as string);
        detailResponse.value = response.data;

        // Fetch state log
        const stateLogResponse = await fetchStateLog(id as string);
        stateLog.value = stateLogResponse.data;

        // Fetch sale status log
        const saleStatusLogResponse = await fetchSaleStatusLog(id as string);
        saleStatusLog.value = saleStatusLogResponse.data;

    } catch (error: any) {
        message.error(error.message);
    }

});






</script>
  
<style scoped lang="scss">
.page {
    .clickable {
        cursor: pointer;
    }

    .n-timeline-item-timeline__circle:hover.filled {
        background-color: #ff5b92
    }

    a {
        color: var(--primary-color);
        text-decoration: none;

    }
}
</style>
  