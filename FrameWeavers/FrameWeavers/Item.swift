//
//  Item.swift
//  FrameWeavers
//
//  Created by chii_magnus on 2025/7/23.
//

import Foundation
import SwiftData

@Model
final class Item {
    var timestamp: Date
    
    init(timestamp: Date) {
        self.timestamp = timestamp
    }
}
