<template>
    <n-grid :x-gap="12">
        <n-grid-item v-for="(field, index) in fields" :key="index" :span="4">
            <n-form-item-gi :show-label="false">
                <n-select @mousedown.native="handleMiddleClick($event, index)" :options="options"
                    v-model:value="fields[index]" :placeholder="`Group #${index + 1}`" />
                <!-- <div class="remove">
                    <small>{{ `Group #${index + 1}` }}</small>
                    <n-button :disabled="!(numOfFields > 1)" text type="primary" @click="removeField(index)">
                        <Icon :size="12" name="carbon:close" />
                    </n-button>
                </div> -->
            </n-form-item-gi>
        </n-grid-item>
        <!-- Add Button -->
        <n-grid-item :span="1">
            <n-button :disabled="!(numOfFields <= 4)" size="medium" dashed type="primary" @click="addField">
                <Icon :size="12" name="carbon:add" />
            </n-button>
        </n-grid-item>
    </n-grid>
</template>
<script setup>
import { ref, watch, defineProps, defineEmits, computed } from 'vue';
import { NDivider, NFormItemGi, NSelect, NButton, NFlex, NGrid, NGridItem } from 'naive-ui';
import Icon from '@/components/common/Icon.vue';

const props = defineProps({
    modelValue: Array,
    options: Array
});



// compute modelValue length
const numOfFields = computed(() => props.modelValue.length);


const emit = defineEmits(['update:modelValue']);

const fields = ref(props.modelValue);

watch(fields, (newValue) => {
    emit('update:modelValue', newValue);
}, { deep: true });

const addField = () => {
    fields.value.push(null); // You might want to initialize it with some value or keep it empty
};

const removeField = (index) => {
    fields.value.splice(index, 1);
};


const handleMiddleClick = (event, index) => {
    event.preventDefault();
    if (event.button === 1 && numOfFields.value > 1) {
        removeField(index);
    }
};

</script>
  

<style lang="scss" scoped>
.remove {
    position: absolute;
    top: -20px;
    right: 0;
}

.tag-fade-enter-active,
.tag-fade-leave-active {
    transition: opacity 0.1s, transform 0.1s;
}

.tag-fade-enter-from,
.tag-fade-leave-to {
    opacity: 0;
    transform: translateX(-10%);
}

.tag-fade-enter-to,
.tag-fade-leave-from {
    opacity: 1;
    transform: translateX(0);
}
</style>