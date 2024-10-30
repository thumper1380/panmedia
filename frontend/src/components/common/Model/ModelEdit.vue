<template>
    <n-drawer :auto-focus="false" class="edit-entity-drawer" resizable :default-width="drawerWidth"
        v-model:show="showDrawer" placement="right" :on-update:show="closeDrawer">
        <n-drawer-content closable>
            <template #header>
                <span class="text-lg font-semibold">Edit Entity</span>
            </template>
            <template #default>
                <n-form :label-width="80" ref="formRef" :model="formModel" :rules="formRules">
                    <div v-for="field in schema" :key="field.key">
                        <n-form-item :label="field.title" :path="field.key" v-if="!field.read_only">
                            <n-input v-if="field.type === FieldType.CharField || field.type === FieldType.EmailField"
                                :placeholder="`Enter ${field.title.toLowerCase()}`" v-model:value="formModel[field.key]" />
                            <n-input v-if="field.type === FieldType.IntegerField"
                                :placeholder="`Enter ${field.title.toLowerCase()}`" v-model:value="formModel[field.key]" />
                            <country-input v-if="field.type === FieldType.CountryField" :filterable="true" :multiple="false"
                                v-model:value="formModel[field.key]" placeholder="Select Country" />
                            <!-- Add other field types here -->
                        </n-form-item>
                    </div>
                </n-form>
                <n-flex :justify="isMobile() ? 'center' : 'flex-end'" :class="isMobile() ? 'mt-5' : 'mt-5'">
                    <n-button :loading="loading" type="primary" @click="submit" :disabled="loading">
                        <span v-if="!loading">Update</span>
                    </n-button>
                </n-flex>
            </template>
        </n-drawer-content>
    </n-drawer>
</template>


<script setup lang="ts">
import { toRefs, ref, defineProps, computed, watch } from 'vue';
import { useMessage, NDrawer, NDrawerContent, NForm, NFormItem, NInput, NButton, NScrollbar, NFlex, type FormInst, type FormRules, type FormValidationError } from 'naive-ui';
import CountryInput from '@/components/CountryInput.vue';
import { FieldType, type Field } from '@/types/fields';
import { isMobile } from '@/utils';
const emit = defineEmits(['update:showDrawer', 'submit']);

const message = useMessage();
const props = defineProps({
    schema: {
        type: Array as () => Array<Field>,
        required: true,
    },
    entityData: { // The initial data for the entity being edited
        type: Object,
        required: true,
    },
    showDrawer: {
        type: Boolean,
        required: true,
    },
    loading: {
        type: Boolean,
        default: false,
    },
});

const { schema, entityData, showDrawer } = toRefs(props);

const formModel = ref({});
const formRef = ref<FormInst | null>(null);
const drawerWidth = computed(() => isMobile() ? '100%' : '30%');

// Initialize formModel with entityData
watch(entityData, (newData) => {
    formModel.value = { ...newData };
}, { immediate: true, deep: true });

// ... (rest of your setup code, including formRules and getFieldRules)
// ... (submit function, closeDrawer function)
const closeDrawer = () => {
    emit('update:showDrawer', false);
};

const submit = (e: Event) => {
    e.preventDefault();
    formRef.value?.validate(async (errors: Array<FormValidationError> | undefined) => {
        if (!errors) {
            console.log('Form is valid, updated model:', JSON.stringify(formModel.value));
            emit('submit', formModel.value);
        } else {
            console.error('Validation errors:', errors);
            message.error('Validation errors occurred');
        }
    });
};



</script>
