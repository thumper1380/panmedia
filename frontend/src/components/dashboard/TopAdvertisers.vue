<template>
    <div class="top-advetisers">
        <CardWrapper v-slot="{ expand, isExpand, reload }">
            <CardActions title="Top Advertisers" :expand="expand" :isExpand="isExpand" :reload="reload">

                <n-scrollbar>
                    <n-table style="table-layout: fixed;">
                        <thead>
                            <tr>
                                <th v-for="column in columns" :key="column.key" :style="{ width: column.width + 'px' }">
                                    {{ column.title }}
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="row in dataSource" :key="row.country">
                                <td v-for="(column, index) in columns" :key="index" :style="{ width: column.width + 'px' }">
                                    <component :is="column.render ? column.render(row, index) : 'span'" />
                                </td>
                            </tr>
                        </tbody>
                    </n-table>
                </n-scrollbar>

            </CardActions>
        </CardWrapper>
    </div>
</template>
  
<script setup lang="ts">
import { reactive, computed, h, toRefs } from 'vue';
import { NTable, NCard, NInputGroup, NInput, NButton, NFlex, NScrollbar, NSpin } from 'naive-ui';
import Icon from '@/components/common/Icon.vue';
import { RouterLink } from 'vue-router';
import CardWrapper from '@/components/common/CardWrapper.vue';
import CardActions from '@/components/common/CardActions.vue';

// loading prop
const props = defineProps({
    loading: {
        type: Boolean,
        default: false
    }
})

const { loading } = toRefs(props)


// Mock data
const data = [
    { advertiser: { id: 1, name: 'Advertiser 1' }, total_clicks: 100, total_leads: 50, total_sales: 25, conversion_rate: 0.25 },
    { advertiser: { id: 2, name: 'Advertiser 2' }, total_clicks: 200, total_leads: 100, total_sales: 50, conversion_rate: 0.50 },
    { advertiser: { id: 3, name: 'Advertiser 3' }, total_clicks: 300, total_leads: 150, total_sales: 75, conversion_rate: 0.75 },
    { advertiser: { id: 4, name: 'Advertiser 4' }, total_clicks: 400, total_leads: 200, total_sales: 100, conversion_rate: 1.00 },
    { advertiser: { id: 5, name: 'Advertiser 5' }, total_clicks: 500, total_leads: 250, total_sales: 125, conversion_rate: 1.25 },
];

const columns = computed(() => [
    {
        title: 'Advertiser',
        key: 'advertiser',
        width: 120,
        render: (row) => {
            let value = row;
            return h(RouterLink, {
                to: {
                    name: 'AdvertiserDetails',
                    params: {
                        id: row.advertiser.id,
                    }
                }
            }, () => row.advertiser.name);
        },
    },
    {
        title: 'Clicks',
        key: 'total_clicks',
        width: 120,
        render: (row) => h('span', `${row.total_clicks}`),
    },
    {
        title: 'Leads',
        key: 'total_leads',
        width: 120,
        render: (row) => h('span', `${row.total_leads}`),
    },
    {
        title: 'Sales',
        key: 'total_sales',
        width: 120,
        render: (row) => h('span', `${row.total_sales}`),
    },
    {
        title: 'CR',
        key: 'conversion_rate',
        width: 120,
        render: (row) => h('span', `${(row.conversion_rate * 100).toFixed(2)}%`),
    },
]);

const dataSource = reactive(data);
</script>
  
<style lang="scss">
/* disable padding on card content */

.top-advetisers {
    // .n-card__content {
    //     padding: 0 !important;
    // }

    a {
        color: var(--primary-color);
        text-decoration: none
    }

}
</style>
  