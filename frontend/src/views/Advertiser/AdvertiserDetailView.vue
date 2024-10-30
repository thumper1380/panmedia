<template>
  <div class="page advertiser-detail-view">
    <ModelDetailView :detail-response="detailResponse" title="Advertiser Detail" />
  </div>
</template>
  
<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { NCard, NDescriptions, NDescriptionsItem } from 'naive-ui';
import type { Advertiser } from '@/types/advertiser';
import type { ApiResponse } from '@/types/response';
import { retrieve } from '@/services/advertiserService';
import { useRoute } from 'vue-router';
import ModelDetailView from '@/components/common/Model/ModelDetailView.vue';
// Sample data, replace with real data
const route = useRoute();


const detailResponse = ref<ApiResponse<Advertiser>>({});

onMounted(async () => {
  const { id } = route.params;
  const response = await retrieve(id as string);
  detailResponse.value = response.data;

});

// You might want to fetch the real advertiser data based on a route parameter or state
</script>
  
<style scoped></style>
  