<script setup>
import { ref } from 'vue'
import NavBar from '@/components/NavBar.vue'

// State for selected AI model
const selectedModel = ref('XGBoost')
</script>

<template>
  <v-app>
    <NavBar :selected-model="selectedModel" />
    <v-main>
      <v-container class="pt-8 px-8" max-width="1280">
        <router-view :selected-model="selectedModel" />
        
        <!-- Copyright Footer -->
        <v-row justify="center" class="no-print">
          <v-col cols="12" class="text-center text-caption text-medium-emphasis">
            © {{ new Date().getFullYear() }} <a href="https://derojas.ai" target="_blank" class="text-medium-emphasis">derojas.ai</a>. All rights reserved.
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<style>
/* Any remaining app-specific styles that can't be handled by Vuetify classes */
@media print {
  .no-print {
    display: none !important;
  }
}
</style>
