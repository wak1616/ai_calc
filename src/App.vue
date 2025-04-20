<script setup>
import { ref } from 'vue'
import NavBar from '@/components/NavBar.vue'

// State for selected AI model
const selectedModel = ref('XGBoost') // MODIFIED: Default to XGBoost

const handleModelUpdate = (newModel) => {
  selectedModel.value = newModel
}
</script>

<template>
  <v-app>
    <NavBar :selected-model="selectedModel" @update:model="handleModelUpdate" />
    <v-main>
      <v-container class="pa-8" max-width="1280">
        <router-view :selected-model="selectedModel" />
      </v-container>
    </v-main>
  </v-app>
</template>

<style>
/* Any remaining app-specific styles that can't be handled by Vuetify classes */
</style>
