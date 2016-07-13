package com.billy.demo.libs.moduleA;

import android.util.Log;

/**
 * module A
 * @author billy.qi
 * @since 16/7/11 17:02
 */
public class ModuleA {

    public ModuleA() {
        Log.i("ModuleA", "ModuleA created");
    }

    public void show() {
        Log.i("ModuleA", "showing...");
    }

    @Override
    public String toString() {
        return "ModuleA";
    }
}
