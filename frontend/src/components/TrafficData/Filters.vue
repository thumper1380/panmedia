<template>
    <n-drawer placement="right" :width="drawerWidth">
        <n-drawer-content closable>
            <template #header>
                <n-flex align="center" justify="center">
                    <Icon name="ion:filter" :size="20" />
                    Filters
                </n-flex>
            </template>
            <n-form>
                <!-- <n-form-item label="Country">
                    <country-input v-model:value="filters.country" filterable multiple />

                </n-form-item>
                <n-form-item label="Affiliate">
                    <api-select-input related-field="affiliate" v-model:value="filters.affiliate" />
                </n-form-item>
                <n-form-item label="Advertiser">
                    <api-select-input related-field="advertiser" v-model:value="filters.advertiser" />
                </n-form-item> -->

                <n-form-item v-for="column in filterableColumns" :key="column.key" :label="column.title">
                    <component :is="getFilterComponent(column)" v-model:value="localFilters[column.key]" />
                </n-form-item>
            </n-form>
            <template #footer>
                <!-- reset -->
                <n-flex>
                    <n-button @click="applyFilters">Reset</n-button>

                    <n-button type="primary" @click="applyFilters">Apply</n-button>
                </n-flex>
            </template>
        </n-drawer-content>
    </n-drawer>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, onMounted, type PropType, toRefs, computed, h, reactive } from 'vue';
import {
    NDrawer,
    NDrawerContent,
    NForm,
    NButton,
    NFlex,
    NFormItem,
    NInput,
    NDatePicker,
    NSelect,
} from 'naive-ui';
import CountryInput from '@/components/CountryInput.vue';
import { isMobile } from '@/utils';
import Icon from '@/components/common/Icon.vue';
import ApiSelectInput from '../common/ApiSelectInput.vue';
const drawerWidth = ref(isMobile() ? '100%' : '350px');
import { FieldType } from '@/types/fields';


// on mounted, apply filters
onMounted(() => {
    // console.log(filters.value);
});

interface Column {
    key: string;
    title: string;
    type: FieldType;
    minWidth: number;
    maxWidth: number;
    width: number;
    resizable: boolean;
    visible: boolean;
    filterable: boolean;
}

const props = defineProps({
    columnsConfig: {
        type: Array as PropType<Column[]>,
        required: true,
    },
    filters: {
        type: Object as PropType<Record<string, any>>,
        default: () => ({}),
    }
});

const { columnsConfig, filters } = toRefs(props);

const localFilters = ref(props.filters || {});



const filterableColumns = computed(() => {
    return columnsConfig.value.filter(column => column.filterable);
});


const getFilterComponent = (column: Column) => {
    // This function will return a VNode
    switch (column.type) {
        case FieldType.CountryField:
            return h(CountryInput, {
                multiple: true,
                filterable: true
            });

        case FieldType.RelatedField:
            return h(ApiSelectInput, {
                relatedField: column.key,
            });

        case FieldType.DateTimeField:
            return h(NDatePicker, {
                clearable: true,
                type: 'daterange',
                style: { width: '100%' },
                monthFormat: 'MMM'
            });

        case FieldType.StateField:
            return h(NSelect, {
                clearable: true,
                style: { width: '100%' },
                multiple: true,
                options: [
                    { label: 'Click', value: 'click' },
                    { label: 'Click Landed', value: 'click_landed' },
                    { label: 'Lead', value: 'lead' },
                    { label: 'Lead Pushed', value: 'lead_pushed' },
                    { label: 'Lead Rejected', value: 'lead_rejected' },
                    { label: 'Sale', value: 'sale' }
                ]
            });

        default:
            return h(NInput);
    }
};



const emit = defineEmits(['update:filters']);

const applyFilters = () => {
    console.log(filters.value);
    emit('update:filters', filters.value);
};
</script>

<style scoped></style>
