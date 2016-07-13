package com.billy.demo.develop;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;

import com.billy.demo.libs.moduleA.ModuleA;
import com.billy.demo.libs.moduleB.ModuleB;
import com.billy.demo.libs.moduleC.ModuleC;

/**
 * @author billy.qi
 * @since 16/7/12 09:35
 */
public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        TextView content = (TextView) findViewById(R.id.content);
        content.append(new ModuleA().toString());
        content.append("\n");
        content.append(new ModuleB().toString());
        content.append("\n");
        content.append(new ModuleC().toString());
        content.append("\n");
    }

}
