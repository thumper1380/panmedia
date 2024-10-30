<template>
    <n-drawer :auto-focus="false" class="add-entity-drawer" resizable :default-width="drawerWidth" v-model:show="showDrawer"
        placement="right" :on-update:show="closeDrawer">
        <n-drawer-content closable>
            <template #header>
                <span class="text-lg font-semibold">Create Entity</span>
            </template>
            <template #default>
                <n-scrollbar>
                    <n-form :label-width="80" ref="formRef" :model="formModel" :rules="formRules">
                        <div v-for="field in schema" :key="field.key">
                            <n-form-item :label="field.title" :path="field.key" v-if="!field.read_only">
                                <n-input v-if="field.type === FieldType.CharField || field.type === FieldType.EmailField"
                                    :placeholder="`Enter ${field.title.toLowerCase()}`"
                                    v-model:value="formModel[field.key]" />
                                <n-input v-if="field.type === FieldType.IntegerField"
                                    :placeholder="`Enter ${field.title.toLowerCase()}`"
                                    v-model:value="formModel[field.key]" />
                                <country-input v-if="field.type === FieldType.CountryField" :filterable="true"
                                    :multiple="false" v-model:value="formModel[field.key]" placeholder="Select Country" />
                                <!-- Add other field types here -->
                            </n-form-item>
                        </div>
                        <n-flex :justify="isMobile() ? 'center' : 'flex-end'" :class="isMobile() ? 'mt-5' : 'mt-5'">
                            <!-- <n-button @click="closeDrawer" :disabled="loading">Cancel</n-button> -->
                            <n-button :loading="loading" type="primary" @click="submit" :disabled="loading">
                                <span v-if="!loading">Submit</span>
                                <!-- <n-spin  size="small" content-style="font-size: 12px">Creating...</n-spin> -->
                            </n-button>
                        </n-flex>
                    </n-form>
                </n-scrollbar>
            </template>
        </n-drawer-content>
    </n-drawer>
</template>
<script setup lang="ts">
import { toRefs, ref, defineProps, computed, watch } from 'vue';
import { NSpin, useMessage, NDrawer, NDrawerContent, NForm, NFormItem, NInput, NButton, NScrollbar, NFlex, type FormInst, type FormRules, type FormValidationError } from 'naive-ui';
import CountryInput from '@/components/CountryInput.vue';
import { FieldType, type Field } from '@/types/fields';
import Icon from '@/components/common/Icon.vue';
import { isMobile } from '@/utils';
const emit = defineEmits(['update:showDrawer', 'submit', 'update:loading']);

const message = useMessage();
const props = defineProps({
    schema: {
        // type: Array of FieldType,
        type: Array as () => Array<Field>,
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

const { schema, showDrawer } = toRefs(props);


const formRef = ref<FormInst | null>(null);
const drawerWidth = computed(() => {
    return isMobile() ? '100%' : '30%';
});


const submit = (e: Event) => {
    e.preventDefault();
    formRef.value?.validate(async (errors: Array<FormValidationError> | undefined) => {
        if (!errors) {
            console.log('Form is valid, model:', JSON.stringify(formModel.value));
            // Handle form submission (e.g., API call)
            emit('submit', formModel.value);
        } else {
            console.error('Validation errors:', errors);
            // message.error('Validation errors occurred');
        }
    });
}





const formModel = ref({});
schema.value.forEach(field => {
    if (!field.read_only) {
        formModel.value[field.key] = ''
    }
});



const formRules = computed(() => {
    const rules = {};
    schema.value.forEach((field: Field) => {
        rules[field.key] = getFieldRules(field);
    });
    return rules;
});

const getFieldRules = (field: Field): FormRules => {
    if (field.read_only) {
        return [];
    }

    const baseRules = [{
        required: true,
        message: `${field.title} is required`,
        trigger: ['input', 'blur']
    }];

    switch (field.type) {
        case 'EmailField':
            return [
                {
                    required: true,
                    validator: (rule, value, callback) => {
                        if (!value) {
                            callback(new Error('Please enter your email address'));
                        } else if (!/\S+@\S+\.\S+/.test(value)) {
                            callback(new Error('Please enter a valid email address'));
                        } else {
                            callback();
                        }
                    },
                    trigger: ['input', 'blur']
                }
            ];
        // Add more cases for other field types if needed
        // case 'SomeOtherFieldType':
        //     return [...baseRules, /* additional rules */];
        default:
            return baseRules;
    }
}




const closeDrawer = () => {
    // Handle drawer close
    console.log('Closing drawer');
    // Add your logic to close the drawer
    emit('update:showDrawer', false);
};

</script>


