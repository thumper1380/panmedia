<template>
    <!-- <n-modal title="Add New Affiliate"> -->
        <n-form ref="formRef" @submit="handleSubmit">
            <n-form-item label="Company Name">
                <n-input v-model:value="affiliate.companyName" placeholder="Enter company name" />
            </n-form-item>
            <n-form-item label="Email">
                <n-input v-model:value="affiliate.email" placeholder="Enter email" />
            </n-form-item>
            <n-form-item label="First Name">
                <n-input v-model:value="affiliate.firstName" placeholder="Enter first name" />
            </n-form-item>
            <n-form-item label="Last Name">
                <n-input v-model:value="affiliate.lastName" placeholder="Enter last name" />
            </n-form-item>
            <n-form-item label="Country">
                <n-input v-model:value="affiliate.country" placeholder="Enter country" />
            </n-form-item>
            <n-form-item label="Telegram">
                <n-input v-model:value="affiliate.telegram" placeholder="Enter Telegram username" />
            </n-form-item>
            <n-form-item label="Skype">
                <n-input v-model:value="affiliate.skype" placeholder="Enter Skype username" />
            </n-form-item>
            <n-button type="primary" @click="handleSubmit">Submit</n-button>
        </n-form>
    <!-- </n-modal> -->
</template>
  
<script setup>
import { defineEmits } from 'vue';
import { NForm, NFormItem, NInput, NButton, NModal } from 'naive-ui';

const props = defineProps({
    showModal: Boolean
});
const emit = defineEmits(['close-modal']);

const formRef = ref(null);
const affiliate = ref({
    companyName: '',
    email: '',
    firstName: '',
    lastName: '',
    country: '',
    telegram: '',
    skype: ''
});

const handleSubmit = () => {
    // ... your submit logic
    emit('close-modal');
};

// Watch for the modal close event to emit close-modal
watch(() => props.showModal, (newVal) => {
    if (!newVal) {
        emit('close-modal');
    }
});
</script>
  
<style scoped>
/* Add your styles here if needed */
</style>
  