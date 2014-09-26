//
//  testLib.m
//  testLib
//
//  Created by riag on 14-9-18.
//  Copyright (c) 2014年 riag. All rights reserved.
//

#import "testLib.h"

@implementation testLib
-(void)Print:(NSString*)msg
{
    printf("===============\n");
    printf("%s\n", [msg cStringUsingEncoding:NSUTF8StringEncoding]);
    printf("===============\n");
}
@end