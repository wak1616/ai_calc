<script setup>
import NavBar from '@/components/NavBar.vue'
</script>

<template>
  <v-app>
    <NavBar />
    <v-main>
      <v-container class="pa-8" max-width="1280">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<style>
/* Any remaining app-specific styles that can't be handled by Vuetify classes */
</style>
