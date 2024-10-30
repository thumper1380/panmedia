<template>
    <n-mention ref="myMention" v-model:value="inputValue" :options="options" :prefix="['{', '=']" @search="handleSearch"
        placeholder="Type { to see options" />
</template>
  
<script setup lang="ts">
import { ref } from 'vue';
import { NMention } from 'naive-ui';
import type { MentionOption, MentionInst } from 'naive-ui/lib/mention/src/interface';

const inputValue = ref();


const clickDataOptions: MentionOption[] = [
    { label: '{{id}}', value: '{id}}' },
    { label: '{{ip_address}}', value: '{ip_address}}' },
    { label: '{{affiliate_id}}', value: '{affiliate_id}}' },
    { label: '{{advertiser_id}}', value: '{advertiser_id}}' }
];

const options = ref<MentionOption[]>([]);



const handleSearch = (_: string, prefix: string) => {
    options.value = clickDataOptions;
};


</script>
  