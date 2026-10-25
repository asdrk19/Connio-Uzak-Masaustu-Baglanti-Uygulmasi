package com.example.bitirme_22;

import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.util.Base64;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Toast;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.constraintlayout.widget.ConstraintLayout;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.WebSocket;
import okhttp3.WebSocketListener;

public class MainActivity extends AppCompatActivity {

    private ImageView screenView;
    private WebSocket webSocket;
    private OkHttpClient client;
    private String SERVER_URL;
    private Button tam_ekran, btnGeri, btnTikla, btnSagTikla;
    private androidx.cardview.widget.CardView screenCard;
    private View controlPanel;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_main);

        if (getSupportActionBar() != null) getSupportActionBar().hide();
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN);

        screenView = findViewById(R.id.screenView);
        screenCard = findViewById(R.id.screenCard);
        controlPanel = findViewById(R.id.control_panel);
        tam_ekran = findViewById(R.id.tam_ekran);
        btnGeri = findViewById(R.id.btn_geri);
        btnTikla = findViewById(R.id.btn_tikla);
        btnSagTikla = findViewById(R.id.btn_sag_tikla);

        Intent intent = getIntent();
        String gelenIp = intent.getStringExtra("vps_ip");
        String gelenPort = intent.getStringExtra("vps_port");

        if (gelenIp == null || gelenIp.isEmpty()) gelenIp = "127.0.0.1";
        if (gelenPort == null || gelenPort.isEmpty()) gelenPort = "8887";

        SERVER_URL = "ws://" + gelenIp + ":" + gelenPort;

        client = new OkHttpClient();
        startWebSocket();

        screenView.setOnTouchListener((v, event) -> {
            if (event.getAction() == MotionEvent.ACTION_DOWN) {
                float percentX = event.getX() / v.getWidth();
                float percentY = event.getY() / v.getHeight();
                sendCoordinates(percentX + "," + percentY);
            }
            return true;
        });
    }

    public void tam_ekran(View view) {
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);

        if (screenCard != null) {
            ConstraintLayout.LayoutParams params = (ConstraintLayout.LayoutParams) screenCard.getLayoutParams();
            params.width = ConstraintLayout.LayoutParams.MATCH_PARENT;
            params.height = ConstraintLayout.LayoutParams.MATCH_PARENT;
            params.setMargins(0, 19, 0, dpToPx(46));
            screenCard.setLayoutParams(params);
        }

        tam_ekran.setVisibility(View.GONE);
        if (controlPanel != null) {
            controlPanel.setVisibility(View.VISIBLE);
        }

        hideSystemUI();
    }

    public void dikey_yap(View view) {
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);

        if (screenCard != null) {
            ConstraintLayout.LayoutParams params = (ConstraintLayout.LayoutParams) screenCard.getLayoutParams();
            params.width = dpToPx(350);
            params.height = dpToPx(250);
            params.setMargins(dpToPx(15), dpToPx(25), dpToPx(15), 0);
            params.bottomToBottom = ConstraintLayout.LayoutParams.UNSET;
            params.topToTop = ConstraintLayout.LayoutParams.PARENT_ID;
            screenCard.setLayoutParams(params);
        }

        tam_ekran.setVisibility(View.VISIBLE);
        if (controlPanel != null) {
            controlPanel.setVisibility(View.GONE);
        }

        showSystemUI();
    }

    public void tikla(View view) {
        new Thread(() -> {
            if (webSocket != null) {
                webSocket.send("double_click");
            }
        }).start();
        Toast.makeText(this, "Çift Tıklandı!", Toast.LENGTH_SHORT).show();
    }

    public void sag_tikla(View view) {
        new Thread(() -> {
            if (webSocket != null) {
                webSocket.send("right_click");
            }
        }).start();
        Toast.makeText(this, "Sağ Tıklandı!", Toast.LENGTH_SHORT).show();
    }

    // --- YENİ EKLENEN POPUP KLAVYE METODU ---
    public void klavye_ac(View view) {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Bilgisayara Metin Gönder");

        // Kullanıcının yazı yazacağı giriş alanı
        final EditText input = new EditText(this);
        input.setHint("Yazmak istediğiniz kelime veya URL...");
        builder.setView(input);

        builder.setPositiveButton("Gönder", (dialog, which) -> {
            String text = input.getText().toString();
            if (!text.isEmpty()) {
                // Sinyalin karışmaması için "write_text:" ön ekiyle gönderiyoruz
                sendSpecialCommand("write_text:" + text);
            }
        });
        builder.setNegativeButton("İptal", (dialog, which) -> dialog.cancel());

        builder.show();
    }

    public void enter_bas(View view) {
        sendSpecialCommand("press_enter");
        Toast.makeText(this, "Klavye: Enter Gönderildi", Toast.LENGTH_SHORT).show();
    }

    public void alt_tab_ya(View view) {
        sendSpecialCommand("alt_tab");
        Toast.makeText(this, "Sistem: Pencere Değiştiriliyor", Toast.LENGTH_SHORT).show();
    }

    public void esc_bas(View view) {
        sendSpecialCommand("press_esc");
        Toast.makeText(this, "Klavye: ESC Gönderildi", Toast.LENGTH_SHORT).show();
    }

    public void cmd_ac(View view) {
        sendSpecialCommand("open_cmd");
        Toast.makeText(this, "Kısayol: CMD Başlatılıyor...", Toast.LENGTH_SHORT).show();
    }

    public void task_manager_ac(View view) {
        sendSpecialCommand("open_taskmgr");
        Toast.makeText(this, "Kısayol: Görev Yöneticisi...", Toast.LENGTH_SHORT).show();
    }

    public void masaustunu_goster(View view) {
        sendSpecialCommand("show_desktop");
        Toast.makeText(this, "Kısayol: Masaüstü...", Toast.LENGTH_SHORT).show();
    }

    private void sendSpecialCommand(String command) {
        new Thread(() -> {
            if (webSocket != null) {
                webSocket.send(command);
            }
        }).start();
    }
    public void motor_calistir(View view){
        System.out.println("Motor aç");
        sendSpecialCommand("motor_ac");
    }
    public void motor_kapat(View view){
        System.out.println("Motor kapat");
        sendSpecialCommand("motor_kapat");
    }

    private int dpToPx(int dp) {
        float density = getResources().getDisplayMetrics().density;
        return Math.round((float) dp * density);
    }

    private void hideSystemUI() {
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
    }

    private void showSystemUI() {
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_VISIBLE);
    }

    private void startWebSocket() {
        Request request = new Request.Builder().url(SERVER_URL).build();
        webSocket = client.newWebSocket(request, new WebSocketListener() {
            @Override
            public void onOpen(WebSocket webSocket, Response response) {
                runOnUiThread(() -> Toast.makeText(MainActivity.this, "Bağlantı Kuruldu!", Toast.LENGTH_SHORT).show());
            }

            @Override
            public void onMessage(WebSocket webSocket, String text) {
                byte[] decodedString = Base64.decode(text, Base64.DEFAULT);
                Bitmap bitmap = BitmapFactory.decodeByteArray(decodedString, 0, decodedString.length);
                runOnUiThread(() -> {
                    if (bitmap != null) screenView.setImageBitmap(bitmap);
                });
            }

            @Override
            public void onFailure(WebSocket webSocket, Throwable t, Response response) {
                runOnUiThread(() -> Toast.makeText(MainActivity.this, "Hata: Sunucuya bağlanılamadı!", Toast.LENGTH_SHORT).show());
            }
        });
    }

    private void sendCoordinates(String coords) {
        new Thread(() -> {
            if (webSocket != null) webSocket.send(coords);
        }).start();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (webSocket != null) webSocket.close(1000, "Uygulama Kapatıldı");
    }
}