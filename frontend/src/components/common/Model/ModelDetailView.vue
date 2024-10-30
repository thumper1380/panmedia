<template>
  <CardWrapper v-slot="{ expand, isExpand, reload }">
    <CardActions :title="title" :subtitle="subtitle" :expand="expand" :isExpand="isExpand" :reload="reload">
      <template #default>
        <n-space vertical :size="12">
          <n-descriptions bordered label-placement="left" :columns="isMobile() ? 1 : 2">
            <n-descriptions-item v-for="column in columnsConfig" :key="column.key" :label="column.title">
              <component :is="render(column)" />
            </n-descriptions-item>
          </n-descriptions>
        </n-space>
      </template>
      <template #action>
        <slot name="action" />
      </template>
    </CardActions>


  </CardWrapper>
</template>

<script setup lang="ts">
import { ref, toRefs, computed, h } from 'vue';
import { NSpace, NDescriptions, NDescriptionsItem } from 'naive-ui';
import CardWrapper from '@/components/common/CardWrapper.vue';
import CardActions from '@/components/common/CardActions.vue';
import { isMobile } from '@/utils';
import renderColumn from '@/utils/table';
import { RouterLink } from 'vue-router';
import type { ApiResponse, Column } from '@/types/response';
const props = defineProps<{
  title?: string;
  subtitle?: string;
  detailResponse: ApiResponse<any>;
}>()

const { detailResponse } = toRefs(props);

const item = computed(() => {
  return detailResponse.value.data;
})
const columnsConfig = computed(() => {
  return detailResponse.value.columns;
})


const render = (column: Column) => {
  const rendered = renderColumn(null, item.value, column);
  return rendered;
}

</script>

<style lang="scss" scoped >
a {
  color: var(--primary-color);
  text-decoration: none;
}
</style>
