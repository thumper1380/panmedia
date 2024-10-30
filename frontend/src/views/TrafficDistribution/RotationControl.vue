<template>
    <div class="page page-wrapped flex flex-col page-without-footer">
        <PageSplitted :sidebarOpen="sidebarOpen" class="rotation-control" @update:sidebarOpen="sidebarOpen = $event">
            <template #main-toolbar>

                <!-- <div style="padding-right: 100px;">
                    <n-scrollbar x-scrollable>
                        <n-breadcrumb>
                            <n-breadcrumb-item>
                                <n-space align="center">
                                    <FolderIcon type="RotationControlAdvertiserFolder" />
                                    Affiliate Folder
                                </n-space>
                            </n-breadcrumb-item>
                            <n-breadcrumb-item>
                                <n-space align="center">
                                    <FolderIcon type="RotationControlAdvertiserFolder" />
                                    Advertiser Folder
                                </n-space>
                            </n-breadcrumb-item>
                        </n-breadcrumb>
                    </n-scrollbar>
                </div> -->
                <n-flex v-if="selectedFolder" justify="center" align="center">
                    <FolderIcon :type="selectedFolder?.type" />
                    <span>
                        {{ selectedFolder?.name }}
                    </span>
                </n-flex>
            </template>
            <template #main-content>
                <div>

                    <!-- <folder-edit :folder="selectedFolder" v-if="selectedFolder" /> -->
                    <FolderPreview :folder="selectedFolder" v-if="selectedFolder" />
                    <!-- <FolderComponent />
                    <FolderComponent />
                    <FolderComponent />
                    <FolderComponent />
                    <FolderComponent /> -->
                </div>
                <!-- <div class="spacer mt-5"></div> -->
            </template>
            <!-- <template #main-footer>Main footer</template> -->
            <template #sidebar-header>
                <div class="section compose-btn-wrap">
                    <n-button @click="createNewFolder" strong secondary type="primary" size="large">
                        New Folder
                    </n-button>
                    <!-- <n-button @click="showModal = true" strong secondary type="primary" size="large">
                        New Folder
                    </n-button> -->
                </div>



            </template>

            <!-- Tree -->

            <template #sidebar-content>
                <n-tree @update:expanded-keys="handleExpandedKeysUpdate" v-model:expanded-keys="expandedKeys"
                    :animated="true" key-field="id" label-field="name" default-expand-all :data="renderTree"
                    :on-update:selected-keys="handleSelectedKeysUpdate" :node-props="nodeProps" block-line>
                    <template #empty>
                        <div class="flex justify-center items-center h-full">
                            <div class="text-center">
                                <div class="text-2xl font-bold mb-2">No folders</div>
                                <div class="text-gray-500">Create a new folder</div>
                            </div>
                        </div>
                    </template>
                </n-tree>
            </template>

        </PageSplitted>
        <!-- <auto-complete-data /> -->
        <n-modal :style="{
            width: '600px'
        }" size="huge" v-model:show="showModal">
            <n-card embedded closable>

                <template #header>
                    <div class="title">
                        Create Rule
                    </div>
                    <!-- <div class="subtitle">
                        
                    </div> -->
                </template>
                <template #default>
                    <FolderSelect />
                </template>
            </n-card>
            <!-- <template #footer>
                <div class="flex justify-end gap-3">
                    <n-button type="primary" @click="showModal = false">Cancel</n-button>
                </div>
            </template> -->
        </n-modal>

        <n-dropdown trigger="manual" placement="bottom-start" :show="showDropdown" :options="(options as any)" :x="x" :y="y"
            @select="handleSelect" @clickoutside="handleClickoutside" />
    </div>
</template>
  
<script setup lang="ts">
import PageSplitted from "@/components/common/PageSplitted.vue";
import { useHideLayoutFooter } from "@/composables/useHideLayoutFooter";
import { NGrid, NGridItem, NButton, NTree, NInput, NFlex, NModal, NCard, NCol, NRow, NSpace, NBreadcrumb, NBreadcrumbItem, NDropdown, type DropdownOption, NScrollbar } from "naive-ui";
import Folder from "@/components/Tree/Folder.vue";
import AutoCompleteData from "@/components/TrAutoCompleteData.vue";
import type { TreeOption } from "naive-ui/lib/tree/src/interface";
import { ref, h, nextTick, onMounted, onBeforeUnmount, computed, onBeforeMount } from "vue";
import FolderEdit from "@/components/Folder/FolderEdit.vue";
import FolderPreview from "@/components/Folder/FolderPreview.vue";
import FolderComponent from "@/components/Folder/FolderComponent.vue";
import Icon from "@/components/common/Icon.vue";
import FolderBox from "@/components/Tree/FolderBox.vue";
import { list } from "@/services/rotationControlService";
import type { TreeFolder, BaseFolder } from '@/types/tree';
import FolderIcon from '@/components/Tree/FolderIcon.vue';
import TargetFolderIcon from "@/components/Tree/TargetFolderIcon.vue";
import { isMobile } from '@/utils';
import FolderSelect from '@/components/Tree/FolderSelect.vue';
import { setActive, remove, create } from "@/services/rotationControlService";
import { renderNode } from '.'
import { TreeFolderType, type CreateFolder, CreateTreeFolderType } from '@/types/tree'

const sidebarOpen = ref(false)



import { useMessage, useDialog } from "naive-ui";


const message = useMessage()
const dialog = useDialog()




const handleClickoutside = () => {
    showDropdown.value = false
}





const handleSelect = (option: string) => {
    if (option == "folder") {
        message.success("New folder")
    }
    else if (option === "delete") {
        dialog.error({
            title: "Delete folder",
            // message that will be shown in the dialog - warn the use that the sub folders will be deleted
            content: "Are you sure you want to delete this folder? All sub folders will be deleted.",
            positiveText: "Delete",
            negativeText: "Cancel",
            onPositiveClick: () => {
                deleteFolder()
            },
        })
    }
    else if (option === "disable") {
        dialog.warning({
            title: "Disable folder",
            // message that will be shown in the dialog - warn the use that the sub folders will be deleted
            content: "Are you sure you want to disable this folder? All sub folders will be disabled.",
            positiveText: "Disable",
            negativeText: "Cancel",
            onPositiveClick: () => {
                setActiveFolder(false)
            },
        })
    }
    else if (option === "enable") {
        dialog.info({
            title: "Enable folder",
            // message that will be shown in the dialog - warn the use that the sub folders will be deleted
            content: "Are you sure you want to enable this folder? All sub folders will be enabled.",
            positiveText: "Enable",
            negativeText: "Cancel",
            onPositiveClick: () => {
                setActiveFolder(true)
            },
        })
    }

    showDropdown.value = false
}

const createNewFolder = async () => {
    const newFolder: CreateFolder = {
        name: "New Folder",
        type: CreateTreeFolderType.CountryFolder,
        countries: ['US'],
        parent: 19
    };

    try {
        const { data } = await create(newFolder);
        if (data.success) {
            const folder = data.data as TreeFolder;
            addNewFolderToTree(folder);
            message.success(`Folder ${folder.name} created`);
        }
        else {
            message.error(`Failed to create folder`);
        }
    } catch (e) {
        message.error(`Failed to create folder`);
    }




}



const setActiveFolder = async (active: boolean) => {
    try {
        const response = await setActive(selectedContextMenuFolder.value?.id as number, active)
        updateFolderStatus(selectedContextMenuFolder.value as TreeFolder, active)
        if (response.data) {
            message.success(`Folder ${selectedContextMenuFolder.value?.name} ${active ? 'enabled' : 'disabled'}`)
        }
    }
    catch (e) {
        // disable update folder status
        updateFolderStatus(selectedContextMenuFolder.value as TreeFolder, !active)
        message.error(`Failed to ${active ? 'enable' : 'disable'} folder ${selectedContextMenuFolder.value?.name}`)
    }
}


const deleteFolder = async () => {
    const tempFolder = selectedContextMenuFolder.value
    try {
        const response = await remove(selectedContextMenuFolder.value?.id as number)
        deleteFoLderFromTree(selectedContextMenuFolder.value as TreeFolder)
        if (response.data) {
            message.success(`Folder ${tempFolder?.name} deleted`)
        }
    }
    catch (e) {
        // addNewFolderToTree(tempFolder as TreeFolder)
        message.error(`Failed to delete folder ${tempFolder?.name}`)
    }
    showDropdown.value = false
}

const selectedFolder = ref<TreeFolder | null>(null)
const options = computed(() => {
    const baseOptions = [
        {
            label: "New",
            key: "new",
            icon: () => h(Icon, { name: "ion:add-outline" }),
            children: [
                {
                    label: "Folder",
                    key: "folder",
                    icon: () => h(Icon, { name: "carbon:folder-add" }),
                },
            ],
        },
    ];

    const statusOption = !selectedContextMenuFolder.value?.disabled
        ? {
            label: "Disable folder",
            key: "disable",
            icon: () => h(Icon, { name: "ion:ban-outline" }),
        }
        : {
            label: "Enable folder",
            key: "enable",
            icon: () => h(Icon, { name: "ion:checkmark-circle-outline" }),
        };

    const deleteOption = {
        label: "Delete folder",
        key: "delete",
        icon: () => h(Icon, { name: "ion:trash-outline" }),
    };

    return selectedContextMenuFolder.value
        ? [...baseOptions, statusOption, deleteOption]
        : baseOptions;
});


const showDropdown = ref(false)
const x = ref(0)
const y = ref(0)



const handleSelectedKeysUpdate = (
    keys: Array<string | number>,
    options: Array<TreeOption | null>,
    meta: { node: TreeOption | null; action: 'select' | 'unselect' }
) => {
    const option = options.filter(Boolean) as TreeFolder[]
    if (option[0]?.id === selectedFolder.value?.id) return
    if (meta.action == 'select') {
        if (option[0] !== null) {
            message.success('[onClick] ' + JSON.stringify(option[0].name))
        }
        sidebarOpen.value = false
        selectedFolder.value = null
        nextTick(() => {
            setTimeout(() => {
                selectedFolder.value = option[0]
            }, 0)

        })
    }
}


const selectedContextMenuFolder = ref<TreeFolder | null>(null)
const expandedKeys = ref<Array<string | number>>([])
const showModal = ref(false)



const getAllFolderIds = (folders: TreeFolder[]): number[] => {
    let ids: number[] = [];
    for (const folder of folders) {
        ids.push(folder.id);
        if (folder.children) {
            ids = ids.concat(getAllFolderIds(folder.children));
        }
    }
    return ids;
};



const handleExpandedKeysUpdate = (keys: Array<string | number>) => {
    expandedKeys.value = keys;
};







const nodeProps = (option: TreeOption) => {
    return {
        onContextmenu(e: MouseEvent): void {
            // options.value = [option]
            e.preventDefault()
            showDropdown.value = false
            selectedContextMenuFolder.value = null
            nextTick(() => {
                x.value = e.clientX
                y.value = e.clientY
                showDropdown.value = true
                selectedContextMenuFolder.value = option.option as TreeFolder
            })

        }
    }
}




const deleteFoLderFromTree = (folder: TreeFolder) => {
    const findAndRemoveFolder = (folderList: TreeFolder[]): TreeFolder[] => {
        return folderList.filter(f => {
            if (f.id === folder.id) {
                return false;
            } else if (f.children && f.children.length > 0) {
                f.children = findAndRemoveFolder(f.children as TreeFolder[]);
                return true;
            } else {
                return true;
            }
        });
    };

    // Update the tree with the modified folder
    tree.value = findAndRemoveFolder(tree.value) as TreeFolder[];
};

const addNewFolderToTree = (folder: TreeFolder) => {
    if (folder.parent_id === null) {
        // Add the new folder to the root level of the tree
        tree.value = [...tree.value, folder];
    } else {
        const findAndAddFolder = (folderList: TreeFolder[]): TreeFolder[] => {
            return folderList.map(f => {
                if (f.id === folder.parent_id) {
                    // Create a new array with the added folder and assign it back to f.children
                    const newChildren = f.children ? [...f.children, folder] : [folder];
                    return { ...f, children: newChildren };
                } else if (f.children && f.children.length > 0) {
                    // Recursively add the new folder to children
                    return { ...f, children: findAndAddFolder(f.children as TreeFolder[]) };
                } else {
                    return f;
                }
            });
        };

        // Update the tree with the modified folder
        tree.value = findAndAddFolder(tree.value) as TreeFolder[];
    }
};



const updateFolderStatus = (folder: TreeFolder, isEnabled: boolean) => {
    const findAndUpdateFolder = (folderList: TreeFolder[]): TreeFolder[] => {
        return folderList.map(f => {
            if (f.id === folder.id) {
                // Update the folder's `disabled` status and all its children
                const updatedFolder = { ...f, disabled: !isEnabled };
                if (updatedFolder.children && updatedFolder.children.length > 0) {
                    updatedFolder.children = updateChildrenStatus(updatedFolder.children as TreeFolder[], !isEnabled);
                }
                return updatedFolder;
            } else if (f.children && f.children.length > 0) {
                // Recursively update children
                return { ...f, children: findAndUpdateFolder(f.children as TreeFolder[]) };
            } else {
                return f;
            }
        });
    };

    const updateChildrenStatus = (children: TreeFolder[], disabled: boolean): TreeFolder[] => {
        return children.map(child => {
            const updatedChild = { ...child, disabled };
            if (updatedChild.children && updatedChild.children.length > 0) {
                updatedChild.children = updateChildrenStatus(updatedChild.children as TreeFolder[], disabled);
            }
            return updatedChild;
        });
    };

    // Update the tree with the modified folder
    tree.value = findAndUpdateFolder(tree.value) as TreeFolder[];
};



// fetch tree folders
const tree = ref<TreeFolder[]>([])

const fetchTree = async () => {
    const { data } = await list()
    tree.value = data.data as TreeFolder[]
}



const renderTree = computed(() => tree.value.map(renderNode));






onBeforeMount(async () => {
    await fetchTree()
    expandedKeys.value = getAllFolderIds(tree.value)
})

onMounted(() => {
    document.querySelector('.rotation-control')?.addEventListener('contextmenu', (e) => {
        e.preventDefault();
    })
})

onBeforeUnmount(() => {
    document.querySelector('.rotation-control')?.removeEventListener('contextmenu', (e) => {
        e.preventDefault();
    })
})


</script>
  
<style lang="scss" scoped>
@import "@/assets/scss/mixin.scss";

.page {
    @media (max-width: 700px) {
        @include page-full-view;
    }


    .toolbar {
        border-block-end: var(--border-small-050);
        min-height: var(--mb-toolbar-height);
        padding: 0 30px;
        gap: 18px;

        .menu-btn,
        .new-btn {
            display: none;
        }

        .search-box {
            margin: 0px 12px;

            .n-input {
                background-color: transparent;
                line-height: 40px;

                :deep() {

                    .n-input__border,
                    .n-input__state-border {
                        display: none;
                    }
                }
            }
        }
    }

    .spacer {
        background: var(--divider-005-color);
        background: repeating-linear-gradient(-45deg,
                var(--divider-005-color),
                var(--divider-005-color) 1px,
                transparent 1px,
                transparent 20px);
        width: 100%;
        height: 200vh;
        border-radius: 14px;
        border: 4px dashed var(--divider-005-color);
        opacity: 0.5;
    }

    .sidebar {
        min-width: 230px;

        .compose-btn-wrap {
            width: 100%;
            height: var(--mb-toolbar-height);
            padding: 0px 15px;
            display: flex;
            align-items: center;
            justify-content: center;

            :deep() {
                .n-button {
                    width: 100%;
                    display: flex;
                    align-items: center;
                    background-color: var(--primary-010-color);

                    .n-button__content {
                        gap: 14px;
                    }
                }
            }
        }

        .folders-list {
            margin-bottom: 20px;

            .folder {
                padding: 10px 22px;
                gap: 14px;
                height: 52px;
                cursor: pointer;
                transition: all 0.25s ease-out;
                opacity: 0.8;
                position: relative;

                .f-icon {
                    display: flex;
                }

                .f-title {
                    font-size: 14px;
                }

                &:hover {
                    background-color: var(--hover-005-color);
                }

                &.f-active {
                    opacity: 1;

                    .f-title {
                        font-weight: bold;
                    }

                    &::before {
                        content: "";
                        width: 4px;
                        height: 20px;
                        background-color: var(--primary-color);
                        position: absolute;
                        top: 50%;
                        transform: translateY(-50%);
                        left: 0;
                        border-top-right-radius: var(--border-radius-small);
                        border-bottom-right-radius: var(--border-radius-small);
                    }
                }
            }
        }

        .labels-list {
            padding: 16px 22px;

            .list {
                .label {
                    cursor: pointer;
                    gap: 8px;
                    margin-bottom: 6px;

                    .l-icon {
                        width: 10px;
                        height: 10px;
                        background-color: var(--color, --primary-color);
                        border-radius: 50%;
                    }

                    .l-title {
                        font-size: 14px;
                        opacity: 0.9;
                        padding-top: 3px;
                        line-height: 1.2;
                    }

                    &:hover {
                        .l-title {
                            opacity: 1;
                        }
                    }

                    &.l-active {
                        .l-title {
                            opacity: 1;
                            font-weight: bold;
                        }
                    }
                }
            }
        }
    }


}
</style>
  