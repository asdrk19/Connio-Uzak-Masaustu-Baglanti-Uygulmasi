package com.example.bitirme_22; // Kendi paket adınla değiştir burayı

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import androidx.appcompat.app.AppCompatActivity;

public class splash extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        // 2 Saniye (2000 milisaniye) sonra başlangıç ekranına geçiş yapar
        new Handler().postDelayed(new Runnable() {
            @Override
            public void run() {
                Intent intent;
                intent = new Intent(splash.this, baslangic_ekrani.class);
                startActivity(intent);
                finish(); // Geri tuşuna basınca tekrar splash ekranına dönmesin diye kapatıyoruz
            }
        }, 2000);
    }
}