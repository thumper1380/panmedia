<template>
    <n-select :size="size" :render-tag="tagRenderer" :render-label="labelRenderer" :multiple="multiple"
        :filterable="filterable" :options="countryOptions" v-model:value="normalizedValue" @update:value="handleUpdate">
    </n-select>
</template>

<script setup lang="ts">
import {
    ref, h, computed, watch, type PropType
} from 'vue';
import { countries } from 'countries-list';
import { NTag, NSelect } from 'naive-ui';
import type { SelectRenderTag, SelectRenderLabel } from 'naive-ui';
import Icon from '@/components/common/Icon.vue';
import type { SelectMixedOption } from 'naive-ui/lib/select/src/interface';

// Types
type SizeType = 'tiny' | 'small' | 'medium' | 'large';
interface CountryOption {
    label: string;
    value: string;
}

const normalizedValue = computed(() => {
    if (props.multiple) {
        return props.value === '' ? [] : props.value;
    }
    return props.value === '' ? null : props.value;
});

// Define component properties
const props = defineProps({
    multiple: {
        type: Boolean,
        default: false
    },
    filterable: {
        type: Boolean,
        default: false
    },
    size: {
        type: String as () => SizeType,
        default: 'medium'
    },
    showFlag: {
        type: Boolean,
        default: true
    },
    value: {
        type: [String, Array] as PropType<string | string[]>,
        default: ''
    }
});


const emit = defineEmits(['update:value']);

const handleUpdate = (value: string | string[]) => {
    emit('update:value', value);
};


// Function to render the label with an optional flag icon
const renderLabel: SelectRenderLabel = (option: any) => {

    return h('div', { style: { display: 'flex', alignItems: 'center' } }, [
        props.showFlag ? h(Icon, { name: `circle-flags:${option.value.toLowerCase()}` }) : undefined,
        h('span', { style: { marginLeft: '8px' } }, option.label)
    ]);
};

// Function to render the tag with a 2-letter country code
const renderTag: SelectRenderTag = ({ option, handleClose }) => {
    return h('div', { style: { display: 'flex', alignItems: 'center' } }, [
        h(NTag, {
            size: 'small',
            closable: true,
            onClose: (e) => {
                e.stopPropagation();
                handleClose();
            }
        }, () => [
            props.showFlag ? h(Icon, { size: 12, name: `circle-flags:${String(option.value).toLowerCase()}` }) : undefined,
            h('span', { style: { marginLeft: '8px' } }, option.value)
        ])
    ]);
};

// Computed properties for conditional rendering
const labelRenderer = computed(() => props.filterable ? renderLabel : undefined);
const tagRenderer = computed(() => {
    if (props.filterable && !props.multiple) return undefined;
    // if only filterable, render tag
    if (props.filterable) return renderTag;

    return undefined;
});
// Convert countries data to options format
const countryOptions = Object.entries(countries).map(([key, value]) => ({
    label: value.name,
    value: key
}) as SelectMixedOption);

</script>
