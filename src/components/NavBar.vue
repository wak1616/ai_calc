<template>
  <!-- The main app bar for larger screens -->
  <v-app-bar 
    color="primary" 
    elevation="2"
  >
    <!-- Mobile menu button -->
    <v-app-bar-nav-icon
      class="d-md-none"
      @click="drawer = !drawer"
      variant="text"
    ></v-app-bar-nav-icon>

    <!-- Brand section -->
    <router-link to="/" class="d-flex align-center text-decoration-none">
      <img
        src="@/assets/derojaslogo.png"
        alt="De Rojas AI Calc"
        class="navbar-logo"
      />
      <span class="site-title text-h4 font-weight-bold">De Rojas AI Calc</span>
    </router-link>

    <!-- Spacer pushes nav items to the right on desktop -->
    <v-spacer />

    <!-- Navigation buttons visible on medium and up screens -->
    <div class="d-none d-md-flex">
      <v-btn
        text
        :class="{ 'text--accent-4': currentRoute === '/' }"
        to="/"
      >
        Home
      </v-btn>

      <!-- AI Model Selector Dropdown (Desktop) -->
      <v-menu>
        <template v-slot:activator="{ props: menuProps }">
          <v-btn
            text
            v-bind="menuProps"
            append-icon="mdi-menu-down"
          >
            AI Model: {{ props.selectedModel }}
          </v-btn>
        </template>
        <v-list density="compact">
          <v-list-item
            v-for="model in aiModels" 
            :key="model"
            :value="model"
            @click="$emit('update:model', model)"
            :active="props.selectedModel === model"
            color="primary"
          >
            <v-list-item-title>{{ model }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>

      <v-btn
        text
        :class="{ 'text--accent-4': currentRoute === '/about' }"
        to="/about"
      >
        About
      </v-btn>

      <!-- Dropdown for Other Resources -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            text
            v-bind="props"
            :class="{ 'text--accent-4': menu }"
          >
            Other Resources
            <v-icon right>mdi-menu-down</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item
            href="https://www.lricalculator.com/"
            target="_blank"
          >
            <v-list-item-title>J&amp;J's LRI Calculator</v-list-item-title>
          </v-list-item>
          <v-list-item
            href="https://lricalc.com/"
            target="_blank"
          >
            <v-list-item-title>The Wörtz-Gupta™ LRI Calculator Formula</v-list-item-title>
          </v-list-item>
          <v-divider />
          <v-list-item
            href="https://www.linkedin.com/in/joaquin-de-rojas-598830268/"
            target="_blank"
          >
            <v-list-item-title>About the creator (LinkedIn page)</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </div>
  </v-app-bar>

  <!-- Navigation drawer for mobile view (only visible on small screens) -->
  <v-navigation-drawer
    v-model="drawer"
    temporary
    class="d-md-none"
  >
    <v-list>
      <v-list-item
        to="/"
        @click="drawer = false"
      >
        <v-list-item-title>Home</v-list-item-title>
      </v-list-item>
      
      <v-list-item
        to="/about"
        @click="drawer = false"
      >
        <v-list-item-title>About</v-list-item-title>
      </v-list-item>

      <!-- AI Model Selector (Mobile Drawer) -->
      <v-list-item>
        <v-list-item-title>
          <v-menu location="right">
            <template v-slot:activator="{ props: menuProps }">
              <v-list-item
                v-bind="menuProps"
                class="pa-0"
              >
                <v-list-item-title>
                  AI Model: {{ props.selectedModel }}
                  <v-icon right>mdi-menu-right</v-icon> 
                </v-list-item-title>
              </v-list-item>
            </template>
            <v-list density="compact">
              <v-list-item
                v-for="model in aiModels" 
                :key="model"
                :value="model"
                @click="$emit('update:model', model); drawer = false"
                :active="props.selectedModel === model"
                color="primary"
              >
                <v-list-item-title>{{ model }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-list-item-title>
      </v-list-item>

      <v-list-item>
        <v-list-item-title>
          <v-menu location="right">
            <template v-slot:activator="{ props }">
              <v-list-item
                v-bind="props"
                class="pa-0"
              >
                <v-list-item-title>
                  Other Resources
                  <v-icon right>mdi-menu-down</v-icon>
                </v-list-item-title>
              </v-list-item>
            </template>
            <v-list>
              <v-list-item
                href="https://www.lricalculator.com/"
                target="_blank"
                @click="drawer = false"
              >
                <v-list-item-title>J&amp;J's LRI Calculator</v-list-item-title>
              </v-list-item>
              <v-list-item
                href="https://lricalc.com/"
                target="_blank"
                @click="drawer = false"
              >
                <v-list-item-title>The Wörtz-Gupta™ LRI Calculator Formula</v-list-item-title>
              </v-list-item>
              <v-divider />
              <v-list-item
                href="https://www.linkedin.com/in/joaquin-de-rojas-598830268/"
                target="_blank"
                @click="drawer = false"
              >
                <v-list-item-title>About the creator (LinkedIn page)</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-list-item-title>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'
import { useRoute } from 'vue-router'

// Define props received from App.vue
const props = defineProps({
  selectedModel: {
    type: String,
    required: true
  }
})

// Define emits sent to App.vue
const emit = defineEmits(['update:model'])

// AI Model options
const aiModels = ref(['Monotonic Neural Network', 'XGBoost'])

// Determine the current route to apply active styling
const route = useRoute()
const currentRoute = computed(() => route.path)

// Menu state for the "Other Resources" dropdown (desktop)
const menu = ref(false)

// Drawer state for the mobile navigation menu
const drawer = ref(false)
</script>

<style scoped>
.site-title {
  letter-spacing: 0.5px;
  color: white;
  font-family: 'Roboto', sans-serif;
  transition: all 0.3s ease;
  opacity: 1;
}

.site-title:hover {
  opacity: 0.8;
}

/* Navbar styles */
.navbar-logo {
  height: 3.5rem;
  width: auto;
  margin-right: 10px;
}
</style>