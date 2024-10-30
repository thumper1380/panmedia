<template>
    <n-select :loading="loading" filterable multiple v-model:value="value" clearable
        :options="localOptions" :placeholder="placeholder" remote @search="handleSearch">

    </n-select>
</template>


<script setup lang="ts">
import { ref, toRefs, computed, onBeforeMount, onMounted } from 'vue';
import { NSelect } from 'naive-ui';
import { options as modelApiOptions, type Option } from '@/services/settingsService';


const value = ref(null);
const options = ref<Option[]>([]);
const props = defineProps({
    relatedField: {
        type: String,
        required: true,
    },
});

const { relatedField } = toRefs(props);

const placeholder = computed(() => {
    return `Select ${relatedField.value}`;
});


const loading = ref(false);

// to naive-ui select options
const localOptions = computed(() => {
    return options.value.map((option) => {
        return {
            label: option.name,
            value: option.id,
        };
    });
});

const fetchOptions = async (query?: string) => {
    loading.value = true;
    const response = await modelApiOptions[relatedField.value as keyof typeof modelApiOptions](query);
    options.value = response.data;
    loading.value = false;
};

const onFocus = async () => {
    if (options.value.length === 0) {
        await fetchOptions();
    }
};

const handleSearch = async (value: string) => {
    if (value.length > 0) {
        await fetchOptions(value);
    }
    else {
        await fetchOptions();
    }
};

onMounted(async () => {
    await fetchOptions();
});

</script>


<style land="scss" scoped></style>