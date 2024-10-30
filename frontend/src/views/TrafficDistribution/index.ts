import { setActive } from "@/services/rotationControlService";
import type { BaseFolder, TreeFolder } from "@/types/tree";
import FolderIcon from '@/components/Tree/FolderIcon.vue';
import TargetFolderIcon from "@/components/Tree/TargetFolderIcon.vue";
import { h } from "vue";

export function renderNode(node: BaseFolder): TreeFolder {
    // return {
    //     name: `${node.name} #${node.id}`,
    //     id: node.id.toString(),
    //     children: node.children ? node.children.map(renderNode) : undefined,
    //     prefix: () => h(Folder, { color: '#00b27b', content: `${node.name[0]}` }),
    // };
    const type = node.type

    switch (type) {
        case 'RotationControlCountryFolder':
            return {
                ...node,
                children: node.children ? node.children.map(renderNode) : undefined,
                prefix: () => h(FolderIcon, { type: type }),
            }
        case 'RotationControlAffiliateFolder':
            return {
                ...node,
                children: node.children ? node.children.map(renderNode) : undefined,
                prefix: () => h(FolderIcon, { type: type }),
            }
        case 'RotationControlAdvertiserFolder':
            return {
                ...node,
                children: node.children ? node.children.map(renderNode) : undefined,
                prefix: () => h(TargetFolderIcon, { type: type }),
            }
        case 'CapFolder':
            return {
                ...node,
                children: node.children ? node.children.map(renderNode) : undefined,
                prefix: () => h(TargetFolderIcon, { type: type }),
                suffix: () => h('small', { style: 'color: var(--n-node-text-color-disabled)' }, '0/1000'),
            }
        case 'RotationControlAdvertiserSplit':
            return {
                ...node,
                children: node.children ? node.children.map(renderNode) : undefined,
                prefix: () => h(TargetFolderIcon, { type: type }),
                suffix: () => h('small', { style: 'color: var(--n-node-text-color-disabled)' }, '100%'),
            }
        default:
            return {
                ...node,
                children: node.children ? node.children.map(renderNode) : undefined,
                prefix: () => h(FolderIcon, { type: type }),
            }
    }

};



