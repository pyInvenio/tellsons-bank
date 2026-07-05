package com.tellsons.fraud;

import java.util.List;

public record SignalDecision(String disposition, int score, List<String> reasons) {
}
