//
//  testFirstViewController.m
//  testAPP
//
//  Created by riag on 14-9-18.
//  Copyright (c) 2014年 riag. All rights reserved.
//

#import "testFirstViewController.h"
#import "testLib.h"

@interface testFirstViewController ()

@end

@implementation testFirstViewController

- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view, typically from a nib.
    testLib* test = [testLib alloc];
    [test Print: @"xxx"];
}

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

@end
