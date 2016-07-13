package com.billy.demo.libs.moduleC;

import android.util.Log;

import com.billy.demo.libs.moduleB.ModuleB;


/**
 * module C
 * @author billy.qi
 * @since 16/7/11 17:02
 */
public class ModuleC {

    public ModuleC() {
        Log.i("ModuleC", "ModuleC created");
    }

    public void show() {
        Log.i("ModuleC", "showing...");
        new ModuleB().show();
    }

    @Override
    public String toString() {
        return "ModuleC";
    }
}
