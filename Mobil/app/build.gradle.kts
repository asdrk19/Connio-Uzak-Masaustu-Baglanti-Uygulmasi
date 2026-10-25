plugins {
    alias(libs.plugins.android.application)
    id("com.google.gms.google-services") // Bunu ekle
}

android {
    namespace = "com.example.bitirme_22"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.bitirme_22"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
}

dependencies {
    implementation(libs.appcompat)
    implementation(libs.material)
    implementation(libs.activity)
    implementation(libs.constraintlayout)

    // Firebase Realtime Database (Bunu ekle)
    implementation("com.google.firebase:firebase-database:20.3.0")

    // OkHttp (WebSocket için zaten eklemişsin)
    implementation(libs.okhttp)

    testImplementation(libs.junit)
    androidTestImplementation(libs.ext.junit)
    androidTestImplementation(libs.espresso.core)
}