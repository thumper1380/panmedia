<template>
    <div class="page">
        <!-- Advertisers Table -->
        <n-card>
            <n-page-header class="mb-5" title="Advertisers">
                <template #extra>
                    <n-tooltip trigger="hover" placement="left">
                        <template #trigger>
                            <n-button type="primary" @click="addAffiliate">
                                <Icon :size="15" name="carbon:add" />
                            </n-button>
                        </template>
                        <template #default>
                            Add Advertiser
                        </template>
                    </n-tooltip>
                </template>
            </n-page-header>
            <n-data-table striped :scroll-x="1800" :data="advertisers" :columns="columns"></n-data-table>
            <n-pagination class="mt-3" :total="advertisers.length" v-model:page="page" :page-size="5" />
        </n-card>
    </div>
</template>

<script setup>
import { ref, h } from 'vue';
import { NPageHeader, NCard, NDataTable, NPagination, NTag, NTooltip, NButton } from 'naive-ui';
import Icon from '@/components/common/Icon.vue';
import { RouterLink } from 'vue-router';

const advertisers = ref([
    // Your advertisers data here...
    // Example:
    { id: 7, name: 'MyDemoAdv', active: 'Active', provider: 'IREV', currency: 'Usd', createdAt: 'Dec. 12, 2023, 4:04 p.m.' },
    { id: 6, name: 'Convertical', active: 'Inactive', provider: 'Test Provider', currency: 'Usd', createdAt: 'Aug. 31, 2023, 11:11 a.m.' },
    // Add more advertisers...
]);

const columns = ref([
    {
        title: 'ID', key: 'id',
        render: (row) => h(RouterLink, { to: `/advertisers/${row.id}` }, { default: () => row.id })
    },
    { title: 'Name', key: 'name' },
    {
        title: 'Status', key: 'active',
        render: (row) => h(NTag, {
            type: row.active === 'Active' ? 'success' : 'error', // Adjust according to your logic
            size: 'small',
        }, { default: () => row.active })
    },
    { title: 'Provider', key: 'provider' },
    { title: 'Default Currency', key: 'currency' },
    { title: 'Created At', key: 'createdAt' },
    // Define more columns here...
]);

const page = ref(1);
</script>

<style lang="scss">
.page {
    a {
        color: var(--primary-color);
        text-decoration: none;
    }
}
</style>
