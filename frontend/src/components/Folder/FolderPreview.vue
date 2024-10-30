<template>
    <div class="folder-preview">
        <n-data-table children-key="childrens" table-layout="fixed" size="large" :columns="columns" :data="processData" />
    </div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, h } from 'vue'
import { NDataTable, NCard, NButton, NInput, NFlex } from 'naive-ui'
import { isMobile } from '@/utils'
import FolderIcon from '@/components/Tree/FolderIcon.vue'
import { TreeFolderType, type TreeFolder } from '@/types/tree'
import Icon from '@/components/common/Icon.vue'
import { useMessage } from 'naive-ui'

const props = defineProps({
    folder: {
        type: Object as () => TreeFolder,
        required: true
    }
})

const { folder } = toRefs(props)

const currentFolder = ref(folder.value)

// compute first level of folders as data
const processData = computed(() => {
    if (!currentFolder.value || !currentFolder.value.children) return []
    return currentFolder.value.children.map((child: any) => {
        return {
            name: child.name,
            description: child.description,
            children: child.children,
            disabled: child.disabled
        }
    })
})

const message = useMessage()
const columns = ref([
    {
        title: 'Name',
        key: 'name',
        width: '20%',
        // render: (row: any) => {
        //     return h(FolderIcon, { type: TreeFolderType.CapFolder, })
        // }
        // add render function to display folder icon and name inside a fle 
        render: (row: any) => {
            return h(NFlex, { direction: 'row', align: 'center' }, () => [
                h(FolderIcon, { type: TreeFolderType.CapFolder }),
                h(NButton, { focusable: false, text: true, onClick: () => onClick(row) }, () => row.name)
            ])
        },
    },
    {
        title: 'Description',
        key: 'description',
        width: '20%',

    },
    // {
    //     key: 'action',
    //     // title: 'Action',
    //     width: '10%',
    //     render: () => {
    //         return h(NButton, { focusable: false, text: true, onClick: () => message.info('You clicked action') }, () => [
    //             h(Icon, { name: 'carbon:pen', size: 16 }),
    //         ])
    //     }
    // }
])




const onClick = (row: any) => {
    currentFolder.value = row
}

</script>


<style lang="scss">
.folder-preview {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    animation: folder-view 0.3s ease-in-out forwards;

    a {
        color: var(--secondary-color) !important;
        text-decoration: none;
    }


    .edit-card {
        min-height: 100%;
    }

    @keyframes folder-preview {
        from {
            transform: translateY(-10%);
            opacity: 0;
        }

        to {
            transform: translateY(0);
            opacity: 1;
        }
    }


}
</style>