package com.example.bitirme_22; // Kendi paket adınla değiştir

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

public class baslangic_ekrani extends AppCompatActivity {

    private EditText etIp, etPort, etKod;
    private Button btnBaglan;
    private DatabaseReference dbRef;

    // Firebase'den gelecek verileri tutacağımız geçici değişkenler
    private String serverIp = "";
    private String serverPort = "";
    private String realConnectionCode = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_baslangic_ekrani);

        // Görsel bileşenleri bağlama
        etIp = findViewById(R.id.et_ip);
        etPort = findViewById(R.id.et_port);
        etKod = findViewById(R.id.et_kod);
        btnBaglan = findViewById(R.id.btn_baglan);

        // PC'deki sunucu.py ile birebir aynı Firebase düğümüne bağlanıyoruz
        dbRef = FirebaseDatabase.getInstance().getReference("baglanti_bilgisi");

        // Firebase'den IP, Port ve Üretilen Kodu anlık otomatik çekme
        dbRef.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(@NonNull DataSnapshot snapshot) {
                if (snapshot.exists()) {
                    serverIp = snapshot.child("ip").getValue(String.class);
                    serverPort = snapshot.child("port").getValue(String.class);
                    realConnectionCode = snapshot.child("kod").getValue(String.class);

                    // Arayüzdeki kutuları otomatik doldur
                    etIp.setText("IP: " + serverIp);
                    etPort.setText("Port: " + serverPort);
                }
            }

            @Override
            public void onCancelled(@NonNull DatabaseError error) {
                Toast.makeText(baslangic_ekrani.this, "Veri okuma hatası!", Toast.LENGTH_SHORT).show();
            }
        });

        // Bağlan butonuna basıldığında Şifre/Kod kontrolü yapma
        btnBaglan.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String girilenKod = etKod.getText().toString().trim();

                if (girilenKod.isEmpty()) {
                    Toast.makeText(baslangic_ekrani.this, "Lütfen 6 haneli kodu girin!", Toast.LENGTH_SHORT).show();
                    return;
                }

                // Bilgisayardaki kod ile telefona girilen kod eşleşiyor mu?
                if (girilenKod.equals(realConnectionCode)) {
                    Toast.makeText(baslangic_ekrani.this, "Bağlantı Başarılı!", Toast.LENGTH_SHORT).show();

                    // Kod doğruysa ana ekran akışına (MainActivity) yönlendiriyoruz
                    Intent intent = new Intent(baslangic_ekrani.this, MainActivity.class);
                    // İhtiyaç duyulursa IP ve Port bilgisini ana ekrana paslayabilirsin
                    intent.putExtra("vps_ip", serverIp);
                    intent.putExtra("vps_port", serverPort);
                    startActivity(intent);
                    finish();
                } else {
                    // Kod yanlışsa hata mesajı ver ve geçişe izin verme
                    Toast.makeText(baslangic_ekrani.this, "Hatalı Bağlantı Kodu! Lütfen tekrar deneyin.", Toast.LENGTH_LONG).show();
                }
            }
        });
    }
}