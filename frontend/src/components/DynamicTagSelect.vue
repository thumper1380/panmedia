<template>
    <div class="flex items-center" :show="options.length">
        <div class="tag-container">
            <!-- <n-space> -->
            <transition-group name="tag-fade" tag="div">
                <n-tag v-for="item in values" :key="item" type="success" size="small" class="mr-2" closable
                    @mouseup="handleMiddleClick($event, item)" @close="handleClose(item)"
                    @mousedown="preventMiddleClickDefault($event)" @contextmenu="e => handleContextMenu(e, item)">
                    {{ optionLabel(item) }}
                </n-tag>
            </transition-group>
            <!-- </n-space> -->
            <!-- Context Menu Dropdown -->
            <n-dropdown 
                :show="showContextMenu" 
                :x="contextMenuX" 
                :y="contextMenuY" 
                :options="contextMenuOptions" 
                @select="handleContextMenuSelect" 
                trigger="manual" 
                placement="bottom-start"
                :on-clickoutside="closeContextMenu"
                :show-arrow="false" 
                :class="['tag-context-menu', { 'tag-context-menu-show': showContextMenu }]"
                >
            </n-dropdown>
        </div>

        <!-- show tags if they are in  -->
        <n-popselect arrow-point-to-center :render="renderLabel" :key="componentKey" @update-value="updateValue"
            :value="values" v-if="availableOptions.length" trigger="click" placement="bottom-start" multiple
            :options="options">
            <n-button @click="dropDownVisible = true" :type="type" :focusable="false" dashed size="small">
                <Icon name="carbon:add" :size="12" />
            </n-button>
        </n-popselect>
    </div>
</template>


<script setup lang="ts">
import { h, ref, computed, nextTick } from 'vue'; // Import the 'emit' function from the Vue composition API
import { NButton, NPopselect, NTag, NDropdown } from 'naive-ui';
import Icon from '@/components/common/Icon.vue';
import type { SelectOption } from 'naive-ui/lib';
const emit = defineEmits(['update:values']);



type option = {
    label: string;
    value: string;
    disabled?: boolean;
}
type type = 'default' | 'primary' | 'success' | 'warning' | 'error' | 'info';

const props = defineProps({
    options: {
        type: Array as () => option[],
        default: () => []
    },
    type: {
        type: String as () => type,
        default: 'default'
    },
    values: {
        type: Array as () => string[],
        default: () => [],
    }
});


const renderLabel = (option: any) => {
    return 'sad'
};

const componentKey = ref(0);


const dropDownVisible = ref(true);

const availableOptions = computed(() => {
    // filter out options that are already selected
    return props.options.filter(option => !props.values.includes(option.value));

});

// compute option label
const optionLabel = (item: any) => {
    return props.options.find((i) => i.value === item)?.label;
};

const handleClose = (item: any) => {
    emit('update:values', props.values.filter((i: any) => i !== item));
};

const updateValue = (value: any) => {
    emit('update:values', value);

    nextTick(() => {
        componentKey.value++; // Increment key to force re-render

    });

};


const handleMiddleClick = (event: any, item: any) => {
    event.preventDefault(); // Prevents default behavior like opening a link in a new tab
    // Check if the middle mouse button was clicked
    if (event.button === 1) {
        handleClose(item);
        event.preventDefault(); // Prevents default behavior like opening a link in a new tab
    }
};


const preventMiddleClickDefault = (event: any) => {
    // Check if the middle mouse button was clicked
    if (event.button === 1) {
        event.preventDefault(); // Prevents default behavior like opening a link in a new tab
    }
};





const showContextMenu = ref(false);
const contextMenuX = ref(0);
const contextMenuY = ref(0);
const contextMenuOptions = ref([{ label: 'Remove', key: 'remove' }]);
const selectedTag = ref(null);

const handleContextMenu = (e, tag: any) => {
    e.preventDefault();
    selectedTag.value = tag;
    showContextMenu.value = false;
    nextTick(() => {
        contextMenuX.value = e.clientX;
        contextMenuY.value = e.clientY;
        showContextMenu.value = true;
    });

}
const closeContextMenu = () => {
    showContextMenu.value = false;
};

const handleContextMenuSelect = (key: string) => {
    switch (key) {
        case 'remove':
            handleClose(selectedTag.value);
            break;
        default:
            break;
    }
    
    closeContextMenu();

};





</script>

<style lang="scss" scoped>
.n-tag {
    margin-right: 8px;
    padding: 14px 10px;
    font-size: 0.7rem;
    font-weight: 500;
    // animation: fade-in 0.3s;
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