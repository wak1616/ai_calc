<template>
  <v-container>
    <v-row>
      <v-col>
        <div class="text-h4 font-weight-medium mb-4">XGBoost AI Calculator</div>
        
        <div class="text-h6 font-weight-regular mb-8 text-medium-emphasis pl-4">Please enter case details below, then submit:</div>
        
        <v-card class="mb-6 pa-4" elevation="2">
          <v-card-text>
            <v-form
              ref="form"
              @submit.prevent="handleSubmit"
              v-model="formValid"
            >
              <div class="mb-4">
                <v-text-field
                  v-model="formData.ID"
                  label="Patient ID"
                  variant="outlined"
                  color="primary"
                  class="input-field"
                  :rules="[rules.required]"
                ></v-text-field>
              </div>

              <div class="mb-4">
                <v-text-field
                  v-model="formData.DOS"
                  label="Date of Surgery"
                  type="date"
                  variant="outlined"
                  color="primary"
                  class="input-field"
                  :rules="[rules.required]"
                ></v-text-field>
              </div>

              <div class="mb-4">
                <v-text-field
                  v-model="formData.age"
                  label="Age (years)"
                  type="number"
                  min="30"
                  max="120"
                  step="1"
                  variant="outlined"
                  color="primary"
                  class="input-field"
                  :rules="[rules.required, rules.ageRange]"
                ></v-text-field>
              </div>

              <div class="mb-4">
                <v-radio-group
                  v-model="formData.eye"
                  label="Eye"
                  inline
                  color="primary"
                  class="mt-2"
                  :rules="[rules.required]"
                >
                  <v-radio
                    label="Right"
                    value="OD"
                    class="me-8"
                  ></v-radio>
                  <v-radio
                    label="Left"
                    value="OS"
                    class="me-8"
                  ></v-radio>
                </v-radio-group>
              </div>

              <div class="py-2">
                <v-text-field
                  v-model="formData.corneal_astigmatism"
                  label="Corneal Astigmatism (D)"
                  type="number"
                  min="0.00"
                  max="1.50"
                  step="0.01"
                  variant="outlined"
                  base-color="primary"
                  class="input-field"
                  :rules="[rules.required, rules.cornealAstigmatismRange]"
                ></v-text-field>
              </div>

              <div class="py-2">
                <v-text-field
                  v-model="formData.steep_axis"
                  label="Steep Axis (°)"
                  type="number"
                  min="0"
                  max="180"
                  step="1"
                  variant="outlined"
                  base-color="primary"
                  class="input-field"
                  :rules="[rules.required, rules.steepAxisRange]"
                ></v-text-field>
              </div>

              <div class="py-2">
                <v-text-field
                  v-model="formData.mean_k"
                  label="Average K (D)"
                  type="number"
                  min="30.00"
                  max="50.00"
                  step="0.01"
                  variant="outlined"
                  base-color="primary"
                  class="input-field"
                  :rules="[rules.required, rules.meanKRange]"
                ></v-text-field>
              </div>

              <div class="py-2">
                <v-text-field
                  v-model="formData.WTW"
                  label="WTW (mm)"
                  type="number"
                  min="10.0"
                  max="15.0"
                  step="0.1"
                  variant="outlined"
                  base-color="primary"
                  class="input-field"
                  :rules="[rules.required, rules.wtwRange]"
                ></v-text-field>
              </div>

              <div class="mt-8">
                <v-btn 
                  type="submit" 
                  color="primary" 
                  size="large"
                  elevation="2"
                  class="px-8"
                  :disabled="!formValid"
                >
                  Submit
                </v-btn>
              </div>
            </v-form>

            <v-fade-transition>
              <v-alert
                v-if="showToricAlert"
                type="warning"
                variant="tonal"
                class="mt-4"
                closable
              >
                High astigmatism noted at this steep axis. Consider a toric IOL as an alernative to arcuate incisions.
              </v-alert>
            </v-fade-transition>

            <v-fade-transition>
              <v-alert
                v-if="errorMessage"
                type="error"
                variant="tonal"
                class="mt-4"
                closable
                @click:close="errorMessage = ''"
              >
                {{ errorMessage }}
              </v-alert>
            </v-fade-transition>

            <v-fade-transition>
              <v-card
                v-if="finalData"
                class="mt-8 bg-grey-darken-3"
                elevation="3"
              >
                <v-card-text>
                  <div class="text-h6" :style="{ color: ARCUATE_COLORS.first }">{{ finalData.arcuate1text }}</div>
                  <div v-if="finalData.arcuate2text" class="text-h6" :style="{ color: ARCUATE_COLORS.second }">{{ finalData.arcuate2text }}</div>
                </v-card-text>
              </v-card>
            </v-fade-transition>

            <v-fade-transition>
              <v-card
                v-if="finalData"
                class="mt-8"
                elevation="2"
              >
                <canvas ref="myCanvas" width="927.67" height="683.67"></canvas>
              </v-card>
            </v-fade-transition>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch, computed } from 'vue'
import leftEyeTemplate from '@/assets/lefteyetemplate.jpg'
import rightEyeTemplate from '@/assets/righteyetemplate.jpg'

const form = ref(null)
const formValid = ref(false)
const errorMessage = ref('')

const formData = reactive({
  ID: '',
  DOS: '',
  age: null,
  eye: '',
  corneal_astigmatism: null,
  steep_axis: null,
  mean_k: null,
  WTW: null
})

const finalData = ref(null)
const myCanvas = ref(null)

const ARCUATE_COLORS = {
  first: '#FFFF00',  // Yellow
  second: '#FFA500'  // Orange
}

const API_URL = 'http://localhost:8000'

const rules = {
  required: value => !!value || 'Required field',
  ageRange: value => {
    const num = Number(value)
    return (num >= 21 && num <= 120) || 'Age must be between 21 and 120 years'
  },
  cornealAstigmatismRange: value => {
    const num = Number(value)
    return (num >= 0.20 && num <= 1.50) || 'Corneal Astigmatism must be between 0.20 and 1.50 D'
  },
  steepAxisRange: value => {
    const num = Number(value)
    return (num >= 0 && num <= 180) || 'Steep Axis must be between 0° and 180°'
  },
  meanKRange: value => {
    const num = Number(value)
    return (num >= 30.00 && num <= 50.00) || 'Average K must be between 30.00 and 50.00 D'
  },
  wtwRange: value => {
    const num = Number(value)
    return (num >= 10.0 && num <= 15.0) || 'WTW must be between 10.0 and 15.0 mm'
  }
}

const showToricAlert = computed(() => {
  const astigmatism = Number(formData.corneal_astigmatism)
  const axis = Number(formData.steep_axis)
  return (astigmatism > 0.75 && (axis > 140 || axis < 40)) || 
         (astigmatism > 1.25 && (axis <= 140 && axis >= 40))
})

// Add watcher for formData changes
watch(formData, () => {
  // Only clear if we already have results showing
  if (finalData.value) {
    finalData.value = null
  }
}, { deep: true })

const drawArcuates = () => {
  if (!myCanvas.value || !finalData.value || !formData.eye) return

  const ctx = myCanvas.value.getContext('2d')
  if (!ctx) return

  const img = new Image()
  img.src = formData.eye === 'OD' ? rightEyeTemplate : leftEyeTemplate

  img.onload = () => {
    // Clear canvas
    ctx.clearRect(0, 0, myCanvas.value.width, myCanvas.value.height)
    
    // Draw background image
    ctx.drawImage(img, 0, 0, myCanvas.value.width, myCanvas.value.height)

    // Check if incisions are needed before drawing arcs
    if (finalData.value.arcuate1text === "No arcuate incision needed") {
      return; // Don't draw arcs if none are needed
    }

    // Draw arcuates
    const radius = 250.3334
    const center = formData.eye === 'OS' ? { x: 484.666, y: 333.000 } : { x: 437.333, y: 341.333 }

    // Draw first arcuate
    ctx.beginPath()
    ctx.arc(center.x, center.y, radius, finalData.value.arc1start, finalData.value.arc1end)
    ctx.strokeStyle = ARCUATE_COLORS.first
    ctx.lineWidth = 10
    ctx.stroke()

    // Draw second arcuate if it exists (paired arcuates)
    if (finalData.value.arcuate2text) {
      ctx.beginPath()
      ctx.arc(center.x, center.y, radius, finalData.value.arc2start, finalData.value.arc2end)
      ctx.strokeStyle = ARCUATE_COLORS.second
      ctx.lineWidth = 10
      ctx.stroke()
    }
  }
}

const handleSubmit = async () => {
  const { valid } = await form.value.validate()
  
  if (!valid) {
    return
  }

  try {
    const response = await fetch(`${API_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
    }

    const fetchedData = await response.json();
    finalData.value = fetchedData;
    errorMessage.value = ''; // Clear any previous errors
    await nextTick();
    drawArcuates();
  } catch (error) {
    console.error('Error during prediction:', error);
    errorMessage.value = error.message || 'Error calculating arcuates. Please try again.';
    finalData.value = null; // Clear any previous results
  }
}

onMounted(() => {
  // Pre-load both images
  const rightImg = new Image()
  const leftImg = new Image()
  rightImg.src = rightEyeTemplate
  leftImg.src = leftEyeTemplate
})
</script>

<style scoped>
.input-field {
  --v-input-control-height: 56px;
  --v-field-padding-bottom: 2px;
  --v-field-padding-top: 2px;
  --v-field-input-padding-top: 8px;
}

.v-text-field :deep(.v-field__outline__start) {
  border-radius: 4px 0 0 4px;
}

.v-text-field :deep(.v-field__outline__end) {
  border-radius: 0 4px 4px 0;
}

.canvas-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
}

canvas {
  width: 100%;
  height: auto;
  background-color: white;
  display: block;
  margin: 0 auto;
}

</style> 