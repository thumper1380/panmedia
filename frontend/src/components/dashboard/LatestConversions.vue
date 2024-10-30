<template>
    <div class="latest-conversions">
        <CardWrapper v-slot="{ expand, isExpand, reload }">
            <CardActions title="Latest Conversions" :expand="expand" :isExpand="isExpand" :reload="reload">
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
import dayjs from "@/utils/dayjs";

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
    {
        id: 1,
        funnel: 'Funnel 1',
        country: 'US',
        advertiser: { id: 1, name: 'Advertiser 1' },
        affiliate: { id: 1, name: 'Affiliate 1' },
        created_at: '2024-02-20:11:00:00:00',
    },
    {
        id: 2,
        funnel: 'Funnel 2',
        country: 'UK',
        advertiser: { id: 2, name: 'Advertiser 2' },
        affiliate: { id: 2, name: 'Affiliate 2' },
        created_at: '2024-02-20:10:00:00:00',
    },
    {
        id: 3,
        funnel: 'Funnel 3',
        country: 'CA',
        advertiser: { id: 3, name: 'Advertiser 3' },
        affiliate: { id: 3, name: 'Affiliate 3' },
        created_at: '2021-10-03',
    },
    {
        id: 4,
        funnel: 'Funnel 4',
        country: 'AU',
        advertiser: { id: 4, name: 'Advertiser 4' },
        affiliate: { id: 4, name: 'Affiliate 4' },
        created_at: '2021-10-04',
    },
    {
        id: 5,
        funnel: 'Funnel 5',
        country: 'IN',
        advertiser: { id: 5, name: 'Advertiser 5' },
        affiliate: { id: 5, name: 'Affiliate 5' },
        created_at: '2021-10-05',
    },
];

const columns = computed(() => [
    {
        title: 'ID',
        key: 'id',
        width: 10,
        render: (row) => h(RouterLink, {
            to: {
                name: 'AffiliateDetails',
                params: {
                    id: row.id,
                }
            }
        }, () => row.id),
    },
    {
        title: 'Funnel',
        key: 'funnel',
        width: 120,
        render: (row) => h('span', row.funnel),
    },
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
        title: 'Advertiser',
        key: 'advertiser',
        width: 120,
        render: (row) => {
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
        title: 'Affiliate',
        key: 'affiliate',
        width: 120,
        render: (row) => {
            return h(RouterLink, {
                to: {
                    name: 'AffiliateDetails',
                    params: {
                        id: row.affiliate.id,
                    }
                }
            }, () => row.affiliate.name);
        },
    },
    {
        title: 'Created At',
        key: 'created_at',
        width: 120,
        render: (row) => {
            let date = dayjs(row.created_at);
            return h('span', date.fromNow());
        },
    },
]);

const dataSource = reactive(data);
</script>
  
<style lang="scss">
/* disable padding on card content */

.latest-conversions {
    // .n-card__content {
    //     padding: 0 !important;
    // }

    a {
        color: var(--primary-color);
        text-decoration: none
    }

}
</style>
  