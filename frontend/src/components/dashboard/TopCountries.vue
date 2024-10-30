<template>
    <div class="top-countries">
        <CardWrapper v-slot="{ expand, isExpand, reload }">
            <CardActions title="Top Countries" :expand="expand" :isExpand="isExpand" :reload="reload">
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


const data = [
    {
        "country": "ES",
        "total_clicks": 67,
        "total_leads": 2,
        "total_sales": 1,
        "total_profit": 200.0,
        "click_to_lead": 0.029850746268656716,
        "conversion_rate": 0.5
    },
    {
        "country": "PL",
        "total_clicks": 0,
        "total_leads": 1,
        "total_sales": 0,
        "total_profit": 0.0,
        "click_to_lead": 0,
        "conversion_rate": 0.0
    },
    {
        "country": "ZA",
        "total_clicks": 1,
        "total_leads": 1,
        "total_sales": 0,
        "total_profit": 0.0,
        "click_to_lead": 1.0,
        "conversion_rate": 0.0
    },
    {
        "country": "PT",
        "total_clicks": 1,
        "total_leads": 1,
        "total_sales": 0,
        "total_profit": 0.0,
        "click_to_lead": 1.0,
        "conversion_rate": 0.0
    },
    {
        "country": "FR",
        "total_clicks": 1,
        "total_leads": 1,
        "total_sales": 0,
        "total_profit": 0.0,
        "click_to_lead": 1.0,
        "conversion_rate": 0.0
    },
]

const columns = computed(() => [
    {
        title: 'Country',
        key: 'country',
        width: 120,
        render: (row) => {
            let value = row.country;
            return h('div', {
                style: {
                    display: 'flex',
                    alignItems: 'center',
                },
            }, [
                h(Icon, {
                    name: `circle-flags:${String(value).toLowerCase()}`,
                    size: 15,
                }),
                h('span', { style: 'margin-left: 10px;' }, `${String(value.toUpperCase())}`),
            ]);
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
        title: 'C2L',
        key: 'click_to_lead',
        width: 120,
        render: (row) => h('span', `${(row.click_to_lead * 100).toFixed(2)}%`),
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
  
<style scoped lang="scss">
/* disable padding on card content */
</style>
  