<template>
  <v-container fluid>
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        <v-alert
          type="info"
          class="mb-4 disclaimer-alert"
          elevation="2"
        >
          This web application is intended for investigational purposes only.
        </v-alert>
        
        <div class="text-h6 font-weight-regular mb-4 text-medium-emphasis pl-4 no-print primary white--text pa-4">
          Please enter case details below, then submit:
        </div>
        
        <v-card class="mb-4 pa-4" elevation="2">
          <v-card-text>
            <v-form
              ref="form"
              @submit.prevent="handleSubmit"
              v-model="formValid"
              class="no-print"
            >
              <!-- Row for Patient Name -->
              <v-row justify="center">
                <v-col cols="12" sm="10" md="10">
                  <v-text-field
                    v-model="formData.name"
                    label="Patient Name"
                    variant="outlined"
                    color="primary"
                    density="compact" 
                    :rules="[rules.required]"
                  ></v-text-field>
                </v-col>
              </v-row>

              <!-- Row for ID and DOS -->
              <v-row justify="center">
                <v-col cols="12" sm="10" md="5">
                  <v-text-field
                    v-model="formData.ID"
                    label="Patient ID"
                    variant="outlined"
                    color="primary"
                    density="compact" 
                    :rules="[rules.required]"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="10" md="5">
                  <v-text-field
                    v-model="formData.DOS"
                    label="Date of Surgery"
                    type="date"
                    variant="outlined"
                    color="primary"
                    density="compact" 
                    :rules="[rules.required]"
                  ></v-text-field>
                </v-col>
              </v-row>

              <!-- Row for Age and Eye -->
              <v-row justify="center" class="align-center my-2">
                <v-col cols="12" sm="10" md="5">
                  <v-text-field
                    v-model="formData.age"
                    label="Age (years)"
                    type="number"
                    min="21" 
                    max="120"
                    step="1"
                    variant="outlined"
                    color="primary"
                    density="compact" 
                    :rules="[rules.required, rules.ageRange]"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="10" md="5">
                  <div class="d-flex align-center" style="gap: 16px;">
                    <span class="eye-inline-label text-body-1 text-medium-emphasis ml-4 eye-label-large">Eye</span>
                    <v-radio-group
                      v-model="formData.eye"
                      inline
                      color="primary"
                      class="mb-0 radio-align"
                      :rules="[rules.required]"
                      style="margin-bottom: 0; align-items: center; display: flex; margin-top: -6px;"
                    >
                      <v-radio
                        label="Right"
                        value="OD"
                        class="me-4 text-medium-emphasis"
                      ></v-radio>
                      <v-radio
                        label="Left"
                        value="OS"
                        class="me-4 text-medium-emphasis"
                      ></v-radio>
                    </v-radio-group>
                  </div>
                </v-col>
              </v-row>

              <!-- Row for Corneal Astigmatism and Steep Axis -->
              <v-row justify="center" style="margin-top: -8px;">
                <v-col cols="12" sm="10" md="5">
                  <v-text-field
                    v-model="formData.corneal_astigmatism"
                    label="Corneal Astigmatism (D)"
                    type="number"
                    min="0.25"
                    max="1.25"
                    step="0.01"
                    variant="outlined"
                    color="primary"
                    density="compact"
                    :rules="[rules.required, rules.cornealAstigmatismRange]"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="10" md="5">
                  <v-text-field
                    v-model="formData.steep_axis"
                    label="Steep Axis (°)"
                    type="number"
                    min="0"
                    max="180"
                    step="1"
                    variant="outlined"
                    color="primary" 
                    density="compact" 
                    :rules="[rules.required, rules.steepAxisRange]"
                  ></v-text-field>
                </v-col>
              </v-row>

              <!-- Row for Mean K and WTW -->
              <v-row justify="center">
                <v-col cols="12" sm="10" md="5">
                  <v-text-field
                    v-model="formData.WTW"
                    label="WTW (mm)"
                    type="number"
                    min="10.0"
                    max="15.0"
                    step="0.1"
                    variant="outlined"
                    color="primary" 
                    density="compact" 
                    :rules="[rules.required, rules.wtwRange]"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="10" md="5">
                  <v-text-field
                    v-model="formData.AL"
                    label="Axial Length (mm)"
                    type="number"
                    min="20.0"
                    max="30.0"
                    step="0.01"
                    variant="outlined"
                    color="primary"
                    density="compact"
                    :rules="[rules.required, value => (value >= 20 && value <= 30) || 'Valid range: 20-30 mm']"
                  ></v-text-field>
                </v-col>
              </v-row>

              <!-- Submit Button - Centered -->
              <v-row justify="center">
                <v-col cols="auto">
                  <div class="mt-4">
                    <v-btn 
                      type="submit" 
                      color="primary" 
                      size="large"
                      elevation="2"
                      class="px-8"
                      :disabled="!formValid || isLoading"
                      :loading="isLoading"
                    >
                      Submit
                    </v-btn>
                  </div>
                </v-col>
              </v-row>
            </v-form>

            <v-fade-transition>
              <v-alert
                v-if="showToricAlert"
                type="warning"
                variant="tonal"
                class="mt-4 no-print"
                closable
                density="comfortable"
                style="white-space: normal; line-height: 1.5;"
              >
                <div class="text-body-1">
                  Large arcuate incisions are NOT the best option to correct higher levels of corneal astigmatism (defined as >= 0.6 ATR or >= 1.1 WTR). This model recommends using a TORIC IOL instead.
                </div>
              </v-alert>
            </v-fade-transition>

            <v-fade-transition>
              <v-alert
                v-if="errorMessage"
                type="error"
                variant="tonal"
                class="mt-4 no-print"
                closable
                @click:close="errorMessage = ''"
              >
                {{ errorMessage }}
              </v-alert>
            </v-fade-transition>
            
            <!-- Print-only patient information -->
            <div class="print-only mt-4">
              <h2 class="text-h5 mb-4">Patient Information</h2>
              
              <!-- Standard layout for larger screens -->
              <table class="patient-info-table standard-table">
                <tbody>
                  <tr>
                    <td><strong>Patient Name:</strong></td>
                    <td>{{ formData.name }}</td>
                    <td><strong>Patient ID:</strong></td>
                    <td>{{ formData.ID }}</td>
                  </tr>
                  <tr>
                    <td><strong>Date of Surgery:</strong></td>
                    <td>{{ formData.DOS }}</td>
                    <td><strong>Age:</strong></td>
                    <td>{{ formData.age }} years</td>
                  </tr>
                  <tr>
                    <td><strong>Eye:</strong></td>
                    <td>{{ formData.eye === 'OD' ? 'Right' : 'Left' }}</td>
                    <td><strong>Corneal Astigmatism:</strong></td>
                    <td>{{ formData.corneal_astigmatism }} D</td>
                  </tr>
                  <tr>
                    <td><strong>Steep Axis:</strong></td>
                    <td>{{ formData.steep_axis }}°</td>
                    <td><strong>WTW:</strong></td>
                    <td>{{ formData.WTW }} mm</td>
                  </tr>
                  <tr>
                    <td><strong>Axial Length:</strong></td>
                    <td>{{ formData.AL }} mm</td>
                    <td></td>
                    <td></td>
                  </tr>
                </tbody>
              </table>
              
              <!-- Mobile-optimized single column layout -->
              <table class="patient-info-table mobile-table">
                <tbody>
                  <tr>
                    <td><strong>Patient Name:</strong></td>
                    <td>{{ formData.name }}</td>
                  </tr>
                  <tr>
                    <td><strong>Patient ID:</strong></td>
                    <td>{{ formData.ID }}</td>
                  </tr>
                  <tr>
                    <td><strong>Date of Surgery:</strong></td>
                    <td>{{ formData.DOS }}</td>
                  </tr>
                  <tr>
                    <td><strong>Age:</strong></td>
                    <td>{{ formData.age }} years</td>
                  </tr>
                  <tr>
                    <td><strong>Eye:</strong></td>
                    <td>{{ formData.eye === 'OD' ? 'Right' : 'Left' }}</td>
                  </tr>
                  <tr>
                    <td><strong>Corneal Astigmatism:</strong></td>
                    <td>{{ formData.corneal_astigmatism }} D</td>
                  </tr>
                  <tr>
                    <td><strong>Steep Axis:</strong></td>
                    <td>{{ formData.steep_axis }}°</td>
                  </tr>
                  <tr>
                    <td><strong>WTW:</strong></td>
                    <td>{{ formData.WTW }} mm</td>
                  </tr>
                  <tr>
                    <td><strong>Axial Length:</strong></td>
                    <td>{{ formData.AL }} mm</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <v-fade-transition>
              <div v-if="finalData" class="mt-8 print-compact">
                <v-card
                  class="bg-grey-darken-3 mb-4 print-dark"
                  elevation="3"
                >
                  <v-card-text>
                    <div class="text-h6" :style="{ color: ARCUATE_COLORS.first }">{{ finalData.arcuate1text }}</div>
                    <div v-if="finalData.arcuate2text" class="text-h6" :style="{ color: ARCUATE_COLORS.second }">{{ finalData.arcuate2text }}</div>
                  </v-card-text>
                </v-card>
                
                <v-card
                  class="mb-4"
                  elevation="2"
                  rounded="lg"
                >
                  <div class="canvas-wrapper">
                    <canvas ref="myCanvas" width="1024" height="1024"></canvas>
                  </div>
                  <div class="text-center pa-2 eye-label">
                    <span class="text-h4 font-weight-bold">
                      {{ formData.eye === 'OD' ? 'RIGHT EYE' : 'LEFT EYE' }}
                    </span>
                  </div>
                </v-card>
                
                <!-- Print-only toric alert -->
                <div v-if="showToricAlert" class="print-only mt-4">
                  <v-alert
                    type="warning"
                    variant="tonal"
                    density="comfortable"
                    class="toric-print-alert"
                  >
                    <div class="text-body-1">
                      Large arcuate incisions are NOT the best option to correct higher levels of corneal astigmatism (defined as >= 0.6 ATR or >= 1.1 WTR). This model recommends using a TORIC IOL instead.
                    </div>
                  </v-alert>
                </div>
                
                <!-- Print button appears only after calculation -->
                <v-row justify="center">
                  <v-col cols="auto">
                    <v-btn
                      color="primary"
                      size="large"
                      class="mt-4 no-print"
                      prepend-icon="mdi-printer"
                      @click="printResults"
                    >
                      Print Results
                    </v-btn>
                  </v-col>
                </v-row>
              </div>
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

const props = defineProps({
  selectedModel: {
    type: String,
    required: true
  }
})

const form = ref(null)
const formValid = ref(false)
const errorMessage = ref('')
const isLoading = ref(false)

const formData = reactive({
  name: '',
  ID: '',
  DOS: '',
  age: null,
  eye: '',
  corneal_astigmatism: null,
  steep_axis: null,
  WTW: null,
  AL: null,
  LASIK: 'no',
})

const finalData = ref(null)
const myCanvas = ref(null)

const ARCUATE_COLORS = {
  first: '#FFFF00',  // Yellow
  second: '#FFA500'  // Orange
}

// Use environment variable for API connection with fallback
const API_URL = ref(import.meta.env.VITE_API_URL || 'http://localhost:8000');

// Function to check if API is available (for user feedback)
const checkApiAvailability = async () => {
  try {
    const response = await fetch(`${API_URL.value}/docs`, { 
      method: 'HEAD',
      mode: 'no-cors' // Just to check if server responds
    });
    return true;
  } catch (error) {
    return false;
  }
};

const rules = {
  required: value => !!value || 'Required field',
  ageRange: value => {
    const num = Number(value)
    return (num >= 21 && num <= 120) || 'Valid range: 21-120 years'
  },
  cornealAstigmatismRange: value => {
    const num = Number(value)
    return (num >= 0.25 && num <= 1.25) || 'Valid range: 0.25-1.25 D'
  },
  steepAxisRange: value => {
    const num = Number(value)
    return (num >= 0 && num <= 180) || 'Valid range: 0-180°'
  },
  wtwRange: value => {
    const num = Number(value)
    return (num >= 10.0 && num <= 15.0) || 'Valid range: 10-15 mm'
  }
}

const showToricAlert = computed(() => {
  const astigmatism = Number(formData.corneal_astigmatism)
  const steepAxis = Number(formData.steep_axis)
  
  // Check if astigmatism is ATR (steep axis between 0-30° or 150-180°)
  const isATR =! (steepAxis >= 40 && steepAxis <= 140)
  const isWTR = (steepAxis >= 40 && steepAxis <= 140)
  
  
  // Show toric alert for:
  // - ATR astigmatism >= 0.6D
  // - WTR astigmatism >= 1.1D
  return (isATR && astigmatism >= 0.6) || (isWTR && astigmatism >= 1.1)
})

// Add watcher for formData changes OR selectedModel prop changes
watch([formData, () => props.selectedModel], () => {
  // Only clear if we already have results showing
  if (finalData.value) {
    finalData.value = null
  }
}, { deep: true })

const drawArcuates = () => {
  if (!myCanvas.value || !finalData.value || !formData.eye) return

  const ctx = myCanvas.value.getContext('2d')
  if (!ctx) return

  // Set responsive canvas dimensions to maintain aspect ratio
  const isMobile = window.innerWidth < 600
  
  // Ensure canvas is square for correct aspect ratio
  myCanvas.value.style.width = isMobile ? '100%' : '500px'
  myCanvas.value.style.aspectRatio = '1 / 1'
  
  // Make sure internal dimensions remain square
  const canvasSize = Math.min(1024, Math.max(window.innerWidth * 0.8, 300))
  if (isMobile) {
    // For mobile, set smaller internal dimensions while keeping aspect ratio
    myCanvas.value.width = canvasSize
    myCanvas.value.height = canvasSize
  }
  
  const img = new Image()
  img.src = formData.eye === 'OD' ? rightEyeTemplate : leftEyeTemplate

  img.onload = () => {
    // Clear canvas
    ctx.clearRect(0, 0, myCanvas.value.width, myCanvas.value.height)
    
    // Draw background image - maintain aspect ratio
    ctx.drawImage(img, 0, 0, myCanvas.value.width, myCanvas.value.height)

    // Check if incisions are needed before drawing arcs
    if (finalData.value.arcuate1text === "No arcuate incision needed") {
      return; // Don't draw arcs if none are needed
    }

    // Calculate scaled radius to match canvas size
    const radius = myCanvas.value.width * 0.35 // Scale radius proportionally to canvas size
    const center = { 
      x: myCanvas.value.width / 2, 
      y: myCanvas.value.height / 2 
    }

    // Draw first arcuate with scaled dimensions
    ctx.beginPath()
    ctx.arc(center.x, center.y, radius, finalData.value.arc1start, finalData.value.arc1end)
    ctx.strokeStyle = ARCUATE_COLORS.first
    ctx.lineWidth = myCanvas.value.width * 0.01 // Scale line width with canvas
    ctx.stroke()

    // Draw second arcuate if it exists (paired arcuates)
    if (finalData.value.arcuate2text) {
      ctx.beginPath()
      ctx.arc(center.x, center.y, radius, finalData.value.arc2start, finalData.value.arc2end)
      ctx.strokeStyle = ARCUATE_COLORS.second
      ctx.lineWidth = myCanvas.value.width * 0.01 // Scale line width with canvas
      ctx.stroke()
    }
  }
}

const printResults = () => {
  // Redraw canvas for printing to ensure correct aspect ratio
  drawArcuates()
  
  // Add a small delay to ensure canvas is properly sized and rendered
  setTimeout(() => {
    window.print()
  }, 200)
}

const handleSubmit = async () => {
  const { valid } = await form.value.validate()
  
  if (!valid) {
    return
  }

  try {
    // Show loading state
    isLoading.value = true;
    errorMessage.value = '';
    
    // Check API availability
    const apiAvailable = await checkApiAvailability();
    if (!apiAvailable) {
      throw new Error('API not available. Please try again later.');
    }
    
    // Prepare data with correct types
    const dataToSend = {
      ID: formData.ID,
      DOS: formData.DOS,
      age: parseInt(formData.age),
      eye: formData.eye,
      corneal_astigmatism: parseFloat(formData.corneal_astigmatism),
      steep_axis: parseFloat(formData.steep_axis),
      WTW: parseFloat(formData.WTW),
      AL: formData.AL !== null ? parseFloat(formData.AL) : null,
      LASIK: formData.LASIK
    };
    
    console.log(`Sending request to ${API_URL.value}/predict with data:`, dataToSend);
    
    const response = await fetch(`${API_URL.value}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      credentials: 'omit', // Don't send credentials for cross-origin requests
      body: JSON.stringify(dataToSend)
    });

    if (!response.ok) {
      let errorText = `HTTP error! Status: ${response.status}`;
      try {
        const errorData = await response.json();
        errorText = errorData.detail || errorText;
      } catch (e) {
        // If JSON parsing fails, use the status text
        errorText = `Error ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorText);
    }

    const fetchedData = await response.json();
    finalData.value = fetchedData;
    await nextTick();
    drawArcuates();
  } catch (error) {
    console.error('Error during prediction:', error);
    errorMessage.value = error.message || 'Error calculating arcuates. Please try again.';
    finalData.value = null; // Clear any previous results
  } finally {
    // Hide loading state when done (success or error)
    isLoading.value = false;
  }
}

// Try to find working API port on component mount
onMounted(async () => {
  // Preload images
  const rightImg = new Image()
  const leftImg = new Image()
  
  rightImg.src = rightEyeTemplate
  leftImg.src = leftEyeTemplate
  
  // Check API availability
  try {
    const apiAvailable = await checkApiAvailability();
    if (apiAvailable) {
      console.log(`Backend API available at ${API_URL.value}`);
    }
  } catch (error) {
    console.error('Error checking API availability:', error);
  }
});
</script>

<style scoped>
/* Custom styles for input-field and border-radius removed */

.v-text-field :deep(.v-field__outline__start) {
  /* border-radius: 4px 0 0 4px; */ /* Removed */
}

.v-text-field :deep(.v-field__outline__end) {
  /* border-radius: 0 4px 4px 0; */ /* Removed */
}

.canvas-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
}

/* Canvas wrapper to maintain aspect ratio */
.canvas-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  padding: 8px;
}

/* Ensure canvas maintains aspect ratio */
canvas {
  width: 100%;
  height: auto !important; /* Force auto height to maintain aspect ratio */
  background-color: white;
  display: block;
  margin: 0 auto;
  border-radius: 16px;
  aspect-ratio: 1 / 1; /* Force 1:1 aspect ratio */
  object-fit: contain; /* Ensure content is contained without stretching */
}

/* Add styling for the eye label */
.eye-label {
  margin-top: 8px;
  background-color: #f5f5f5;
  border-top: 1px solid #e0e0e0;
}

/* Print-specific styles */
@media print {
  .no-print {
    display: none !important;
  }
  
  .print-only {
    display: block !important;
  }
  
  /* Show/hide appropriate tables based on screen size */
  @media (max-width: 480px) {
    .standard-table {
      display: none !important;
    }
    
    .mobile-table {
      display: table !important;
    }
  }
  
  @media (min-width: 481px) {
    .standard-table {
      display: table !important;
    }
    
    .mobile-table {
      display: none !important;
    }
  }
  
  /* Fixed page size to prevent unnecessary page breaks */
  @page {
    size: auto; /* Or try 'letter', 'A4' */
    margin: 6mm; /* Further reduced margin */
  }

  body {
    margin: 0;
    padding: 0;
    background-color: white;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    width: 100% !important;
  }

  .v-container {
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    page-break-inside: avoid !important; /* Avoid break inside container */
  }

  /* Apply to the main column holding the content */
  .v-col {
     page-break-inside: avoid !important;
  }
  
  .v-card {
    box-shadow: none !important;
    border: 1px solid #eee;
    margin-bottom: 8px !important; /* Balanced margin */
    padding: 0 !important;
    border-radius: 8px !important; /* Smaller radius */
    overflow: hidden !important;
    page-break-inside: avoid !important; /* Avoid break inside cards */
    width: 100% !important;
  }
  
  .print-dark {
    background-color: #333 !important;
    color: white !important;
    padding: 8px !important; /* Reduced padding for arcuate text */
  }
  
  .print-dark .v-card-text {
    padding: 8px !important; /* Reduced padding */
  }
  
  .print-dark .text-h6 {
    font-size: 15px !important; /* Slightly larger font for arcuate text */
    line-height: 1.3 !important;
    margin-bottom: 3px !important;
  }
  
  .canvas-wrapper {
    width: 100% !important;
    max-width: 350px !important; /* Larger canvas for better visibility */
    margin: 0 auto !important;
    aspect-ratio: 1 / 1 !important;
    padding: 6px !important; /* Slightly more padding */
  }
  
  canvas {
    max-width: 100% !important;
    height: auto !important;
    aspect-ratio: 1 / 1 !important;
    object-fit: contain !important;
    margin: 0 auto !important;
    page-break-inside: avoid !important;
    display: block !important;
    border-radius: 8px !important;
  }
  
  /* Other print optimizations */
  .text-h4 {
    font-size: 18px !important; /* Readable title size */
    margin-bottom: 4px !important;
  }
  
  .eye-label {
    margin-top: 3px !important;
    padding: 4px 0 !important; /* More breathing room */
    background-color: #f0f0f0 !important;
    border-radius: 0 0 8px 8px !important; /* Match card radius */
  }
  
  .eye-label span {
    font-size: 18px !important; /* Larger, more readable title */
    font-weight: bold !important;
    letter-spacing: 0.4px; /* Slightly more spacing */
  }
  
  /* Prevent page breaks */
  .v-application__wrap,
  .v-main,
  .v-main__wrap {
    height: auto !important;
    min-height: auto !important;
    overflow: visible !important;
    page-break-after: avoid !important;
    page-break-before: avoid !important;
    page-break-inside: avoid !important;
  }
  
  /* Patient Info Table adjustments */
  .patient-info-table {
    margin-bottom: 8px !important; /* Slightly more space */
    page-break-inside: avoid !important;
    width: 100% !important;
    table-layout: fixed !important;
    font-size: 10pt !important; /* More readable font */
  }
  
  .patient-info-table td {
    padding: 3px 6px !important; /* Slightly more padding */
    font-size: 10pt !important; /* More readable font */
    word-break: break-word !important;
    vertical-align: top !important;
    line-height: 1.3 !important;
  }
  
  /* Mobile-specific adjustments */
  @media (max-width: 600px) {
    .canvas-wrapper {
      max-width: 200px !important;
    }
    
    canvas {
      width: 100% !important;
      height: auto !important;
      max-height: none !important;
    }
    
    .patient-info-table {
      font-size: 8pt !important;
      border-collapse: collapse !important;
    }
    
    .patient-info-table td {
      padding: 2px 3px !important;
      font-size: 8pt !important;
      line-height: 1.2 !important;
    }
    
    .eye-label span {
      font-size: 14px !important;
    }
    
    /* Alternative single-column mobile layout */
    @media (max-width: 480px) {
      .patient-info-table tr td:nth-child(3),
      .patient-info-table tr td:nth-child(4) {
        display: none !important;
      }
      
      .patient-info-table tr:nth-child(even) {
        background-color: #f8f8f8 !important;
      }
      
      .patient-info-table td {
        width: 50% !important;
      }
      
      /* Ensure the canvas is fully visible */
      canvas {
        width: 100% !important;
        height: auto !important;
        max-height: 180px !important;
      }
    }
  }
}

/* Always hide initially */
.print-only {
  display: none;
}

/* Patient information table for print view */
.patient-info-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
}

.patient-info-table td {
  padding: 5px 10px;
}

.patient-info-table tr:nth-child(even) {
  background-color: #f5f5f5;
}

.eye-inline-label {
  min-width: 48px;
  display: flex;
  align-items: flex-end;
  height: 40px;
  margin-top: -32px;
  font-size: 18px;
}

.radio-align {
  margin-top: -18px !important;
}

.eye-label-large {
  font-size: 1.15rem !important;
}

.disclaimer-alert {
  background-color: #e3f2fd !important; /* Light blue */
  color: #1976d2 !important;           /* Dark blue text for contrast */
  border-left: 6px solid #bbdefb !important; /* Medium blue border */
}

  /* Mobile table is hidden by default */
.mobile-table {
  display: none;
}

/* Print-specific styles for toric alert */
@media print {
  .toric-print-alert {
    background-color: #fff3cd !important;
    border: 1px solid #ffc107 !important;
    border-left: 4px solid #ff9800 !important;
    border-radius: 6px !important;
    padding: 8px 10px !important; /* More readable padding */
    margin: 5px 0 !important; /* Slightly more margin */
    page-break-inside: avoid !important;
    box-shadow: none !important;
  }
  
  .toric-print-alert .text-body-1 {
    color: #856404 !important;
    font-size: 10pt !important; /* More readable font */
    line-height: 1.4 !important;
    margin: 0 !important;
    font-weight: 500 !important;
  }
  
  /* Ensure toric alert fits on mobile print */
  @media (max-width: 600px) {
    .toric-print-alert {
      padding: 4px 6px !important;
      margin: 2px 0 !important;
    }
    
    .toric-print-alert .text-body-1 {
      font-size: 8pt !important;
      line-height: 1.2 !important;
    }
  }
  
  /* Compact spacing for print results section */
  .print-compact {
    margin-top: 6px !important; /* Less compressed spacing */
  }
}
</style> 