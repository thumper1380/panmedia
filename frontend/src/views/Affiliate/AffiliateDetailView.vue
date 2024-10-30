<template>
    <div class="page">
        <ModelDetial :detail-response="detailResponse" title="Affiliate Detail" />
    </div>
</template>
  
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { retrieve } from '@/services/affiliateService';
import type { Affiliate } from '@/types/affiliate';
import ModelDetial from '@/components/common/Model/ModelDetailView.vue';
import type { ApiResponse } from '@/types/response';


const route = useRoute();

const editAffiliateDrawer = ref(false);

const editAffiliate = () => {
    editAffiliateDrawer.value = true;

}


const detailResponse = ref<ApiResponse<Affiliate>>({});

onMounted(async () => {
    const { id } = route.params;
    const response = await retrieve(id as string);
    detailResponse.value = response.data;

});


</script>
  
<style lang="scss" scoped>
@import "@/assets/scss/mixin.scss";

.page {
    // @media (max-width: 700px) {
    //     @include page-full-view;
    // }
}
</style>
  